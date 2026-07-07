"""Chapter 6: turn a real digital DDR into a scanned-style example, then
show why OCR is needed and how the quality gate scores the result.

This archive is 100% digital, so there is no real scanned FORGE report to
work with. This script MAKES one from a real report: it rasterizes the
page to an image and writes it back out as an image-only PDF -- pictures
of text with no character data, exactly what a page scanned from paper
looks like to software. Then it shows the difference: pdfplumber recovers
nothing from the scanned version, OCR recovers the text, and the quality
gate scores both.

Requirements (Chapter 6 only):
    pip install pytesseract pdf2image
    # plus the system tools they wrap:
    #   macOS:  brew install tesseract poppler
    #   Ubuntu: apt install tesseract-ocr poppler-utils

Usage:
    python code/chapter_06/make_scanned_example.py
"""

import sys
from pathlib import Path

import pdfplumber
import pytesseract
from pdf2image import convert_from_path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_quality_gate import evaluate_ocr_quality  # noqa: E402

SRC_PDF = Path("datasets/sample_ddrs/FORGE-16A-78-32_Drilling_038_2020-11-26.pdf")
SCANNED_PDF = Path("datasets/_scanned_example_038.pdf")
STUCK_LINE = "During the slide lost tool face and became assembly became stuck"


def make_scanned_pdf(src_pdf: Path, dest_pdf: Path, dpi: int = 200) -> None:
    """Rasterize every page of a digital PDF and save the images back out
    as an image-only PDF -- a PDF with pictures of text and no character
    data, the way a scan of a paper report looks to software."""
    images = convert_from_path(str(src_pdf), dpi=dpi)
    images[0].save(dest_pdf, save_all=True, append_images=images[1:])


def extract_text(pdf_path: Path) -> str:
    """Chapter 1's digital text extraction, inlined."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n\n".join((page.extract_text() or "") for page in pdf.pages)


def ocr_pdf(pdf_path: Path, dpi: int = 200) -> str:
    """Rasterize each page and run OCR (tesseract) to recover its text."""
    images = convert_from_path(str(pdf_path), dpi=dpi)
    return "\n\n".join(pytesseract.image_to_string(image) for image in images)


if __name__ == "__main__":
    if not SRC_PDF.exists():
        raise SystemExit(f"{SRC_PDF} not found -- see Appendix A for the sample archive.")

    make_scanned_pdf(SRC_PDF, SCANNED_PDF)
    print(f"Wrote image-only (scanned-style) PDF -> {SCANNED_PDF}\n")

    digital = extract_text(SRC_PDF)
    scanned = extract_text(SCANNED_PDF)   # pdfplumber on the image-only PDF
    recovered = ocr_pdf(SCANNED_PDF)      # OCR the same image-only PDF

    print(f"Digital extraction:  {len(digital):5d} chars   stuck line present: {STUCK_LINE in digital}")
    print(f"pdfplumber on scan:  {len(scanned):5d} chars   stuck line present: {STUCK_LINE in scanned}")
    print(f"OCR on scan:         {len(recovered):5d} chars   stuck line present: "
          f"{'became stuck' in recovered.lower()}")

    print("\nQuality gate:")
    for label, text in [("digital", digital), ("OCR", recovered)]:
        result = evaluate_ocr_quality(text)
        print(f"  {label:8s} reject={result['reject_ocr']}  flags={result['flags']}")
