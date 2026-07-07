"""Tests for code/chapter_06/make_scanned_example.py.

The whole OCR round-trip depends on external tools (tesseract + poppler)
and the pytesseract/pdf2image bindings, which are Chapter-6-only extras.
Skip cleanly when any of them is missing, rather than failing the suite
for readers who didn't install them.
"""

import shutil

import pytest

pytest.importorskip("pytesseract")
pytest.importorskip("pdf2image")


@pytest.mark.slow
def test_scanned_roundtrip_defeats_extraction_but_ocr_recovers_it(tmp_path, sample_ddrs_dir):
    if shutil.which("tesseract") is None or shutil.which("pdftoppm") is None:
        pytest.skip("tesseract/poppler system tools not installed")

    from make_scanned_example import extract_text, make_scanned_pdf, ocr_pdf

    src = sample_ddrs_dir / "FORGE-16A-78-32_Drilling_038_2020-11-26.pdf"
    scanned = tmp_path / "scanned.pdf"
    make_scanned_pdf(src, scanned)

    # pdfplumber recovers nothing from an image-only PDF -- that's the whole
    # reason OCR is needed.
    assert extract_text(scanned).strip() == ""

    # OCR reads the real stuck-pipe line back off the page image.
    recovered = ocr_pdf(scanned)
    assert "became stuck" in recovered.lower()
