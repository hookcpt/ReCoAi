# Content Enricher Service

Standalone Python-Mikroservice unter `services/content-enricher` zur Anreicherung von Gambio-Produkt-CSV-Dateien.

## Features
- Isoliert vom restlichen Repository lauffähig
- CLI-first (`enrich` Kommando)
- Sichere CSV I/O (Input bleibt unverändert)
- Modi: `fill-only`, `improve-weak`, `features-only`
- Dry-Run Unterstützung
- Zielspalten:
  - `p_desc.de`
  - `p_shortdesc.de`
  - `p_checkout_information.de`
- Fügt Metadaten-Spalten hinzu:
  - `content_status`
  - `content_source_url`
  - `content_source_type`
  - `content_confidence`
  - `content_template`
  - `content_last_generated_at`
  - `needs_review`
  - `content_notes`

## Installation
```bash
cd services/content-enricher
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Konfiguration
- YAML: `config/settings.yaml`, `config/templates.yaml`
- ENV: siehe `.env.example`

## Nutzung
```bash
content-enricher enrich --input tests/fixtures/sample_products.csv --output /tmp/enriched.csv --mode fill-only --no-llm
content-enricher enrich --input tests/fixtures/sample_products.csv --output /tmp/enriched.csv --mode improve-weak --dry-run --no-llm
content-enricher enrich --input tests/fixtures/sample_products.csv --output /tmp/enriched.csv --mode features-only --no-llm
```

## Designhinweise
- Web-Recherche ist deterministisch begrenzt (Top-3 URLs, Whitelist, reduzierte Inhalte).
- LLM wird nur für Textgenerierung eingesetzt (nicht für freie Suche).
- Provider-Abstraktion vorbereitet, erste Implementierung: Gemini.
- Kategorie-Templates sind YAML-basiert erweiterbar ohne Codeänderung.

## Tests
```bash
pytest
```

## TODO
- TODO(API): HTTP API Modus ergänzen (FastAPI o.ä.)
- TODO(Integration): Direkte Pipeline-Integration in Import/Update-Jobs ergänzen
