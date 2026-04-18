from __future__ import annotations


class QueryBuilder:
    def build(self, row: dict[str, str]) -> str:
        sku = row.get("products_model", "").strip()
        name = row.get("products_name.de", "").strip() or row.get("products_name", "").strip()
        brand = row.get("manufacturer_name", "").strip()
        parts = [p for p in [brand, name, sku] if p]
        return " ".join(parts)
