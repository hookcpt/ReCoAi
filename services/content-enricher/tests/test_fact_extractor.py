from app.extractors.spec_extractor import SpecExtractor


def test_extract_from_attributes_blob():
    row = {"attributes": "Leistung:750W;Spannung:230V"}
    facts = SpecExtractor().extract_from_row(row)
    assert facts["Leistung"] == "750W"
    assert facts["Spannung"] == "230V"
