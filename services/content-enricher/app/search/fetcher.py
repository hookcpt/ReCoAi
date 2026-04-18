from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


class WebSearcher:
    def __init__(self, timeout: int, user_agent: str):
        self.timeout = timeout
        self.user_agent = user_agent

    def _get(self, url: str) -> str:
        req = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(req, timeout=self.timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")

    def search(self, query: str, max_results: int = 3) -> list[str]:
        if not query:
            return []
        url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        text = self._get(url)
        links: list[str] = []
        for part in text.split('class="result__a"'):
            marker = 'href="'
            if marker in part:
                href = part.split(marker, 1)[1].split('"', 1)[0]
                if href.startswith("http") and href not in links:
                    links.append(href)
            if len(links) >= max_results * 2:
                break
        return links[: max_results * 2]


class PageFetcher:
    def __init__(self, cache_dir: Path, timeout: int, user_agent: str):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.user_agent = user_agent

    def fetch(self, url: str) -> str:
        cache_key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_file = self.cache_dir / f"page_{cache_key}.json"
        if cache_file.exists():
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            return payload.get("content", "")

        req = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(req, timeout=self.timeout) as resp:
            text = resp.read().decode("utf-8", errors="ignore")

        cache_file.write_text(json.dumps({"url": url, "content": text}), encoding="utf-8")
        return text
