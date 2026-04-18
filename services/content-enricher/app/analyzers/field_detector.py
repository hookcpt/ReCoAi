from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TargetFields:
    long_desc: str = "p_desc.de"
    short_desc: str = "p_shortdesc.de"
    features: str = "p_checkout_information.de"


class FieldDetector:
    def detect(self, columns: list[str]) -> TargetFields:
        fields = TargetFields()
        # Future TODO: fuzzy matching for custom exports/API mode.
        for col in columns:
            if col.strip().lower() == "p_desc.de":
                fields.long_desc = col
            elif col.strip().lower() == "p_shortdesc.de":
                fields.short_desc = col
            elif col.strip().lower() == "p_checkout_information.de":
                fields.features = col
        return fields
