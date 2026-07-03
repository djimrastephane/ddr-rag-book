"""Chapter 1: extract text from a Daily Drilling Report PDF.

This is the first working artifact of the book: a script that takes a
single DDR PDF and prints (or saves) its raw text content.

Usage:
    python code/chapter_01/read_ddr.py datasets/sample_ddrs/DDR_017_EXAMPLE-1H.pdf
    python code/chapter_01/read_ddr.py datasets/sample_ddrs/ --batch
"""

import argparse
import sys
from pathlib import Path

import pdfplumber


def extract_text(pdf_path: Path) -> str:
    """Return all text found in a PDF, one page after another."""
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_text.append(f"--- Page {page_number} ---\n{text}")
    return "\n\n".join(pages_text)


def process_file(pdf_path: Path, output_dir: Path | None) -> None:
    text = extract_text(pdf_path)

    if not text.strip():
        print(f"[warning] No extractable text in {pdf_path.name} "
              f"— it may be a scanned image. See Chapter 6 for OCR.", file=sys.stderr)

    if output_dir is None:
        print(f"===== {pdf_path.name} =====")
        print(text)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / (pdf_path.stem + ".txt")
        out_file.write_text(text, encoding="utf-8")
        print(f"Wrote {out_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from DDR PDFs.")
    parser.add_argument("path", type=Path, help="Path to a PDF file, or a folder if --batch is used")
    parser.add_argument("--batch", action="store_true", help="Treat 'path' as a folder of PDFs")
    parser.add_argument("--out", type=Path, default=None, help="Folder to save .txt files instead of printing")
    args = parser.parse_args()

    if args.batch:
        pdf_files = sorted(args.path.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDFs found in {args.path}", file=sys.stderr)
            sys.exit(1)
        for pdf_path in pdf_files:
            process_file(pdf_path, args.out)
    else:
        process_file(args.path, args.out)


if __name__ == "__main__":
    main()
