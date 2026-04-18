from __future__ import annotations


class FactNormalizer:
    def normalize(self, facts: dict[str, str]) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for key, value in facts.items():
            k = " ".join(key.split()).strip().lower()
            v = " ".join((value or "").split()).strip()
            if not k or not v:
                continue
            normalized[k] = v
        return normalized
