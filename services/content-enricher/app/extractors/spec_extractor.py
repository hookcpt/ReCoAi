from __future__ import annotations

import re


class SpecExtractor:
    def extract_from_row(self, row: dict[str, str]) -> dict[str, str]:
        facts: dict[str, str] = {}
        candidate_keys = [k for k in row.keys() if any(x in k.lower() for x in ["spec", "eigenschaft", "material", "farbe", "gewicht", "maß"]) ]
        for key in candidate_keys:
            val = (row.get(key) or "").strip()
            if val:
                facts[key] = val

        attr_blob = row.get("attributes", "")
        for pair in re.split(r"[;|]", attr_blob):
            if ":" in pair:
                k, v = pair.split(":", 1)
                if k.strip() and v.strip():
                    facts[k.strip()] = v.strip()
        return facts

    def extract_from_cleaned_page(self, cleaned: dict[str, str | list[str]]) -> dict[str, str]:
        facts: dict[str, str] = {}
        for row in cleaned.get("spec_rows", []):
            if isinstance(row, str) and ":" in row:
                k, v = row.split(":", 1)
                if k.strip() and v.strip():
                    facts[k.strip()] = v.strip()

        bullets = cleaned.get("bullets", [])
        if isinstance(bullets, list):
            for idx, bullet in enumerate(bullets[:8], 1):
                facts[f"bullet_{idx}"] = bullet
        return facts
