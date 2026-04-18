from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class QualityResult:
    is_empty: bool
    is_too_short: bool
    is_generic: bool
    duplicated_with_other: bool

    @property
    def weak(self) -> bool:
        return self.is_empty or self.is_too_short or self.is_generic or self.duplicated_with_other


class QualityChecker:
    GENERIC_PATTERNS = [
        r"hochwertig",
        r"beste qualität",
        r"top produkt",
        r"ideal für",
    ]

    def assess_long(self, text: str, other_text: str = "") -> QualityResult:
        return self._assess(text, min_words=80, compare_to=other_text)

    def assess_short(self, text: str, other_text: str = "") -> QualityResult:
        return self._assess(text, min_words=20, compare_to=other_text)

    def assess_features(self, text: str) -> QualityResult:
        return self._assess(text, min_words=8, compare_to="")

    def _assess(self, text: str, min_words: int, compare_to: str) -> QualityResult:
        cleaned = (text or "").strip()
        words = re.findall(r"\w+", cleaned, flags=re.UNICODE)
        is_empty = not cleaned
        is_too_short = len(words) < min_words if not is_empty else True
        low = cleaned.lower()
        is_generic = any(re.search(p, low) for p in self.GENERIC_PATTERNS)
        duplicated = bool(cleaned and compare_to and self._normalize(cleaned) == self._normalize(compare_to))
        return QualityResult(
            is_empty=is_empty,
            is_too_short=is_too_short,
            is_generic=is_generic,
            duplicated_with_other=duplicated,
        )

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())
