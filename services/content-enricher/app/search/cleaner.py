from __future__ import annotations

import re


def _strip_tags(html: str) -> str:
    html = re.sub(r"<script[\\s\\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\\s\\S]*?</style>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\\s+", " ", text).strip()


class HtmlCleaner:
    def clean(self, html: str) -> dict[str, str | list[str]]:
        html = html or ""
        title_match = re.search(r"<title[^>]*>([\\s\\S]*?)</title>", html, flags=re.IGNORECASE)
        h1_match = re.search(r"<h1[^>]*>([\\s\\S]*?)</h1>", html, flags=re.IGNORECASE)
        li_matches = re.findall(r"<li[^>]*>([\\s\\S]*?)</li>", html, flags=re.IGNORECASE)
        p_matches = re.findall(r"<p[^>]*>([\\s\\S]*?)</p>", html, flags=re.IGNORECASE)
        row_matches = re.findall(r"<tr[^>]*>([\\s\\S]*?)</tr>", html, flags=re.IGNORECASE)

        bullets = [_strip_tags(m) for m in li_matches if _strip_tags(m)][:10]
        paragraphs = [_strip_tags(m) for m in p_matches if _strip_tags(m)][:8]

        spec_rows: list[str] = []
        for row in row_matches:
            cols = re.findall(r"<(?:th|td)[^>]*>([\\s\\S]*?)</(?:th|td)>", row, flags=re.IGNORECASE)
            cols = [_strip_tags(c) for c in cols if _strip_tags(c)]
            if len(cols) >= 2:
                spec_rows.append(f"{cols[0]}: {cols[1]}")

        return {
            "title": _strip_tags(title_match.group(1)) if title_match else "",
            "h1": _strip_tags(h1_match.group(1)) if h1_match else "",
            "bullets": bullets,
            "paragraphs": paragraphs,
            "spec_rows": spec_rows[:12],
        }
