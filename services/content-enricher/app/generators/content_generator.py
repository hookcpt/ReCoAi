from __future__ import annotations

import json
from datetime import datetime, timezone

from app.clients.base import LLMClient
from app.generators.prompt_builder import PromptBuilder


class ContentGenerator:
    def __init__(self, client: LLMClient):
        self.client = client
        self.prompt_builder = PromptBuilder()

    def generate(self, product: dict[str, str], facts: dict[str, str], template: dict[str, str]) -> dict[str, str]:
        if not facts:
            return {
                "long_desc": "",
                "short_desc": "",
                "features_html": "",
                "needs_review": "true",
                "notes": "Nicht genügend Fakten für sichere Generierung.",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        system_prompt, user_prompt = self.prompt_builder.build(product, facts, template)
        raw = self.client.generate(system_prompt, user_prompt)
        data = json.loads(raw)
        data["generated_at"] = datetime.now(timezone.utc).isoformat()
        return data
