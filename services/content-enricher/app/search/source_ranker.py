from __future__ import annotations

from urllib.parse import urlparse


class SourceRanker:
    def __init__(self, approved_domains: list[str], manufacturer_patterns: list[str]):
        self.approved_domains = approved_domains
        self.manufacturer_patterns = [p.lower() for p in manufacturer_patterns]

    def rank(self, urls: list[str]) -> list[str]:
        filtered = [u for u in urls if self._approved(u)]
        filtered.sort(key=self._score, reverse=True)
        return filtered[:3]

    def _approved(self, url: str) -> bool:
        if not self.approved_domains:
            return True
        host = urlparse(url).netloc.lower()
        return any(host == d or host.endswith(f".{d}") for d in self.approved_domains)

    def _score(self, url: str) -> int:
        host = urlparse(url).netloc.lower()
        score = 1
        if any(p in host for p in self.manufacturer_patterns):
            score += 5
        if host.endswith(".de"):
            score += 1
        return score
