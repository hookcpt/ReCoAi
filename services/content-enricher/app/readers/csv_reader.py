from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


class CsvReader:
    def read(self, input_path: str) -> tuple[list[dict[str, str]], list[str]]:
        path = Path(input_path)
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
            return rows, list(reader.fieldnames or [])

    def iter_rows(self, input_path: str) -> Iterable[dict[str, str]]:
        path = Path(input_path)
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield dict(row)
