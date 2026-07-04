"""Tests for code/chapter_06/ocr_quality_gate.py."""


def test_clean_text_passes_the_quality_gate():
    from ocr_quality_gate import evaluate_ocr_quality

    text = "During the slide lost tool face and became assembly became stuck. " * 5
    result = evaluate_ocr_quality(text)

    assert result["reject_ocr"] is False


def test_garbled_text_is_rejected():
    from ocr_quality_gate import evaluate_ocr_quality

    garbled = "D1r+ s1d3 l0st t00l f@c3 !!!@#$%^&*()<>?~`{}[]|\\" * 3
    result = evaluate_ocr_quality(garbled)

    assert result["reject_ocr"] is True
    assert result["flags"]["low_text_density"] is True
    assert result["flags"]["high_symbol_ratio"] is True
