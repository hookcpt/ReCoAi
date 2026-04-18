from __future__ import annotations

import csv
from pathlib import Path


class CsvWriter:
    def write(self, output_path: str, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
