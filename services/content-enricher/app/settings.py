from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


@dataclass
class SearchSettings:
    enabled: bool = False
    approved_domains: list[str] = field(default_factory=list)
    manufacturer_priority_patterns: list[str] = field(default_factory=list)
    max_results: int = 3
    timeout_seconds: int = 8
    user_agent: str = "content-enricher/0.1"


@dataclass
class LLMSettings:
    provider: str = "gemini"
    model: str = "gemini-1.5-flash"
    api_key: str | None = None
    temperature: float = 0.2
    max_output_tokens: int = 800
    debug_traces: bool = False


@dataclass
class TemplateSettings:
    default_category: str = "generic"
    categories: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class ServiceSettings:
    search: SearchSettings = field(default_factory=SearchSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    templates: TemplateSettings = field(default_factory=TemplateSettings)
    cache_dir: Path = Path("cache")


def _load_yaml(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        raw = f.read()
    if yaml:
        data = yaml.safe_load(raw) or {}
    else:
        data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must be object at root: {path}")
    return data


def load_settings(config_path: str | None = None, template_path: str | None = None) -> ServiceSettings:
    config_data = _load_yaml(Path(config_path)) if config_path else {}
    template_data = _load_yaml(Path(template_path)) if template_path else {}

    search_cfg = config_data.get("search", {})
    llm_cfg = config_data.get("llm", {})

    settings = ServiceSettings(
        search=SearchSettings(
            enabled=bool(search_cfg.get("enabled", os.getenv("ENRICHER_SEARCH_ENABLED", "false").lower() == "true")),
            approved_domains=search_cfg.get("approved_domains", []),
            manufacturer_priority_patterns=search_cfg.get("manufacturer_priority_patterns", []),
            max_results=int(search_cfg.get("max_results", os.getenv("ENRICHER_MAX_SEARCH_RESULTS", 3))),
            timeout_seconds=int(search_cfg.get("timeout_seconds", os.getenv("ENRICHER_TIMEOUT", 8))),
            user_agent=search_cfg.get("user_agent", os.getenv("ENRICHER_USER_AGENT", "content-enricher/0.1")),
        ),
        llm=LLMSettings(
            provider=llm_cfg.get("provider", os.getenv("ENRICHER_LLM_PROVIDER", "gemini")),
            model=llm_cfg.get("model", os.getenv("ENRICHER_LLM_MODEL", "gemini-1.5-flash")),
            api_key=os.getenv("GEMINI_API_KEY") or llm_cfg.get("api_key"),
            temperature=float(llm_cfg.get("temperature", os.getenv("ENRICHER_TEMPERATURE", 0.2))),
            max_output_tokens=int(llm_cfg.get("max_output_tokens", os.getenv("ENRICHER_MAX_OUTPUT_TOKENS", 800))),
            debug_traces=bool(llm_cfg.get("debug_traces", os.getenv("ENRICHER_DEBUG_TRACES", "false").lower() == "true")),
        ),
        templates=TemplateSettings(
            default_category=template_data.get("default_category", "generic"),
            categories=template_data.get("categories", {}),
        ),
        cache_dir=Path(config_data.get("cache_dir", os.getenv("ENRICHER_CACHE_DIR", "cache"))),
    )
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    return settings
