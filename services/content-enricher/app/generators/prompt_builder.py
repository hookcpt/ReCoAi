from __future__ import annotations

import json


class PromptBuilder:
    SYSTEM = (
        "Du bist ein deutscher E-Commerce-Texter. Nutze ausschließlich übergebene Fakten. "
        "Keine erfundenen technischen Daten. Wenn Fakten fehlen, markiere needs_review=true."
    )

    def build(self, product: dict[str, str], facts: dict[str, str], template: dict[str, str]) -> tuple[str, str]:
        user_payload = {
            "task": "Erzeuge JSON mit Feldern long_desc, short_desc, features_html, needs_review, notes.",
            "constraints": {
                "language": "de",
                "long_desc_words": "120-180",
                "short_desc_words": "25-45",
                "features_count": "5-8",
            },
            "product": {
                "name": product.get("products_name.de") or product.get("products_name"),
                "brand": product.get("manufacturer_name", ""),
                "sku": product.get("products_model", ""),
                "category": product.get("categories_name.de", "generic"),
            },
            "template": template,
            "facts": facts,
        }
        return self.SYSTEM, json.dumps(user_payload, ensure_ascii=False)
