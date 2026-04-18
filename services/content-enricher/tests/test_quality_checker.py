from app.analyzers.quality_checker import QualityChecker


def test_detects_empty_and_short_long_text():
    qc = QualityChecker()
    r = qc.assess_long("")
    assert r.is_empty is True
    assert r.is_too_short is True


def test_detects_duplicate_short_desc():
    qc = QualityChecker()
    text = "Dies ist ein kurzer Text mit genug Zeichen"
    r = qc.assess_short(text, text)
    assert r.duplicated_with_other is True
