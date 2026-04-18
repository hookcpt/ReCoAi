from pathlib import Path

from app.readers.csv_reader import CsvReader
from app.writers.csv_writer import CsvWriter


def test_read_write_roundtrip(tmp_path: Path):
    sample = Path("tests/fixtures/sample_products.csv")
    rows, cols = CsvReader().read(str(sample))
    assert len(rows) == 2
    out = tmp_path / "out.csv"
    CsvWriter().write(str(out), rows, cols)
    rows2, cols2 = CsvReader().read(str(out))
    assert cols == cols2
    assert rows2[0]["products_model"] == "SKU-1"
