from __future__ import annotations

import argparse
from pathlib import Path

from app.clients.gemini_client import GeminiClient
from app.generators.content_generator import ContentGenerator
from app.pipelines.enrich_pipeline import EnrichPipeline, METADATA_COLUMNS
from app.readers.csv_reader import CsvReader
from app.settings import load_settings
from app.writers.csv_writer import CsvWriter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CSV Content Enricher")
    sub = parser.add_subparsers(dest="command", required=True)

    enrich = sub.add_parser("enrich", help="Enrich product CSV")
    enrich.add_argument("--input", required=True, help="Input CSV path")
    enrich.add_argument("--output", required=True, help="Output CSV path")
    enrich.add_argument("--mode", choices=["fill-only", "improve-weak", "features-only"], default="fill-only")
    enrich.add_argument("--dry-run", action="store_true")
    enrich.add_argument("--config", default="config/settings.yaml")
    enrich.add_argument("--templates", default="config/templates.yaml")
    enrich.add_argument("--no-llm", action="store_true", help="Disable LLM generation")
    return parser


def run_enrich(args: argparse.Namespace) -> int:
    settings = load_settings(config_path=args.config, template_path=args.templates)
    reader = CsvReader()
    writer = CsvWriter()
    rows, columns = reader.read(args.input)

    generator = None
    if not args.no_llm and settings.llm.provider == "gemini":
        client = GeminiClient(
            api_key=settings.llm.api_key or "",
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            max_output_tokens=settings.llm.max_output_tokens,
        )
        generator = ContentGenerator(client)

    pipeline = EnrichPipeline(settings=settings, generator=generator)
    result = pipeline.run(rows, columns, mode=args.mode, dry_run=args.dry_run)

    output_columns = list(columns)
    for c in METADATA_COLUMNS:
        if c not in output_columns:
            output_columns.append(c)

    writer.write(args.output, result.rows, output_columns)
    print(f"Processed rows: {len(rows)} | changed: {result.changed_count} | dry-run={args.dry_run}")
    print(f"Output written to: {Path(args.output).resolve()}")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "enrich":
        raise SystemExit(run_enrich(args))


if __name__ == "__main__":
    main()
