from __future__ import annotations


class TemplateEngine:
    def resolve(self, category: str, all_templates: dict[str, dict]) -> tuple[str, dict]:
        if category in all_templates:
            return category, all_templates[category]
        return "generic", all_templates.get("generic", {"tone": "sachlich", "sections": ["Einleitung", "Details", "Anwendung"]})
