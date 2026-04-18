from __future__ import annotations

from dataclasses import dataclass

from app.analyzers.field_detector import FieldDetector
from app.analyzers.quality_checker import QualityChecker
from app.extractors.fact_normalizer import FactNormalizer
from app.extractors.spec_extractor import SpecExtractor
from app.generators.content_generator import ContentGenerator
from app.generators.template_engine import TemplateEngine
from app.search.cleaner import HtmlCleaner
from app.search.fetcher import PageFetcher, WebSearcher
from app.search.query_builder import QueryBuilder
from app.search.source_ranker import SourceRanker
from app.settings import ServiceSettings


METADATA_COLUMNS = [
    "content_status",
    "content_source_url",
    "content_source_type",
    "content_confidence",
    "content_template",
    "content_last_generated_at",
    "needs_review",
    "content_notes",
]


@dataclass
class PipelineResult:
    rows: list[dict[str, str]]
    changed_count: int


class EnrichPipeline:
    def __init__(self, settings: ServiceSettings, generator: ContentGenerator | None = None):
        self.settings = settings
        self.field_detector = FieldDetector()
        self.quality = QualityChecker()
        self.spec_extractor = SpecExtractor()
        self.normalizer = FactNormalizer()
        self.template_engine = TemplateEngine()
        self.query_builder = QueryBuilder()
        self.searcher = WebSearcher(timeout=settings.search.timeout_seconds, user_agent=settings.search.user_agent)
        self.ranker = SourceRanker(settings.search.approved_domains, settings.search.manufacturer_priority_patterns)
        self.fetcher = PageFetcher(settings.cache_dir, settings.search.timeout_seconds, settings.search.user_agent)
        self.cleaner = HtmlCleaner()
        self.generator = generator

    def run(self, rows: list[dict[str, str]], columns: list[str], mode: str = "fill-only", dry_run: bool = False) -> PipelineResult:
        fields = self.field_detector.detect(columns)
        changed = 0
        out_rows: list[dict[str, str]] = []

        for row in rows:
            updated = dict(row)
            long_text = row.get(fields.long_desc, "")
            short_text = row.get(fields.short_desc, "")
            features_text = row.get(fields.features, "")

            long_q = self.quality.assess_long(long_text, short_text)
            short_q = self.quality.assess_short(short_text, long_text)
            feat_q = self.quality.assess_features(features_text)

            needs = self._needs_enrichment(mode, long_q.weak, short_q.weak, feat_q.weak)
            if not needs:
                updated.update({"content_status": "unchanged", "content_notes": "Keine Anreicherung nötig."})
                out_rows.append(updated)
                continue

            facts = self.normalizer.normalize(self.spec_extractor.extract_from_row(row))
            source_url = ""
            source_type = "csv"
            confidence = 0.7 if facts else 0.2

            if confidence < 0.5 and self.settings.search.enabled:
                query = self.query_builder.build(row)
                urls = self.ranker.rank(self.searcher.search(query, self.settings.search.max_results))
                if urls:
                    source_url = urls[0]
                    source_type = "web"
                    cleaned = self.cleaner.clean(self.fetcher.fetch(urls[0]))
                    web_facts = self.normalizer.normalize(self.spec_extractor.extract_from_cleaned_page(cleaned))
                    facts = {**facts, **web_facts}
                    confidence = 0.8 if web_facts else confidence

            generated = {
                "long_desc": long_text,
                "short_desc": short_text,
                "features_html": features_text,
                "needs_review": "true" if confidence < 0.6 else "false",
                "notes": "LLM deaktiviert oder nicht nötig.",
                "generated_at": "",
            }
            template_name, template_data = self.template_engine.resolve(
                row.get("categories_name.de", self.settings.templates.default_category),
                self.settings.templates.categories,
            )
            if self.generator:
                generated = self.generator.generate(row, facts, template_data)

            if not dry_run:
                if mode != "features-only" and (long_q.weak or mode == "improve-weak"):
                    updated[fields.long_desc] = generated.get("long_desc", long_text)
                if mode != "features-only" and (short_q.weak or mode == "improve-weak"):
                    updated[fields.short_desc] = generated.get("short_desc", short_text)
                if feat_q.weak or mode in {"features-only", "improve-weak"}:
                    updated[fields.features] = generated.get("features_html", features_text)

            updated.update(
                {
                    "content_status": "enriched" if not dry_run else "would_enrich",
                    "content_source_url": source_url,
                    "content_source_type": source_type,
                    "content_confidence": f"{confidence:.2f}",
                    "content_template": template_name,
                    "content_last_generated_at": generated.get("generated_at", ""),
                    "needs_review": str(generated.get("needs_review", "true")).lower(),
                    "content_notes": generated.get("notes", ""),
                }
            )
            changed += 1
            out_rows.append(updated)

        return PipelineResult(rows=out_rows, changed_count=changed)

    def _needs_enrichment(self, mode: str, long_weak: bool, short_weak: bool, feat_weak: bool) -> bool:
        if mode == "fill-only":
            return long_weak or short_weak or feat_weak
        if mode == "improve-weak":
            return long_weak or short_weak or feat_weak
        if mode == "features-only":
            return feat_weak
        raise ValueError(f"Unsupported mode: {mode}")
