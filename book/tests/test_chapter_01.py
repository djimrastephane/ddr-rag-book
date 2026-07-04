"""Tests for code/chapter_01/read_ddr.py against the real sample archive."""


def test_extract_text_contains_the_real_stuck_pipe_sentence(report_038_pdf):
    from read_ddr import extract_text

    text = extract_text(report_038_pdf)

    assert "RPT DATE:11/26/2020" in text
    assert "During the slide lost tool face and became assembly became stuck" in text


def test_extract_text_labels_each_page(report_038_pdf):
    from read_ddr import extract_text

    text = extract_text(report_038_pdf)

    assert "--- Page 1 ---" in text
