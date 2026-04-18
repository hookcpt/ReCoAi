from app.pipelines.enrich_pipeline import EnrichPipeline
from app.readers.csv_reader import CsvReader
from app.settings import load_settings


def test_e2e_enrich_without_llm(tmp_path):
    rows, columns = CsvReader().read("tests/fixtures/sample_products.csv")
    settings = load_settings("config/settings.yaml", "config/templates.yaml")
    pipeline = EnrichPipeline(settings=settings, generator=None)

    result = pipeline.run(rows, columns, mode="fill-only", dry_run=False)
    assert result.changed_count >= 1
    first = result.rows[0]
    assert "content_status" in first
    assert "content_confidence" in first
