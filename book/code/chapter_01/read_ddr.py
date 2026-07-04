"""Chapter 1: extract text from a Daily Drilling Report PDF.

This is the first working artifact of the book: a script that takes a
single DDR PDF and prints (or saves) its raw text content.

Usage:
    python code/chapter_01/read_ddr.py datasets/sample_ddrs/FORGE-16A-78-32_Drilling_038_2020-11-26.pdf
    python code/chapter_01/read_ddr.py datasets/sample_ddrs/ --batch --out datasets/ddr_text
"""

import argparse
import sys
from pathlib import Path

import pdfplumber


def extract_text(pdf_path: Path) -> str:
    """Return all text found in a PDF, one page after another.

    A DDR is usually one page, but this loops over every page so the
    same function works for longer reports too. Each page is prefixed
    with a marker (e.g. "--- Page 1 ---") so that later chapters can
    cite exactly which page a piece of text came from.
    """
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # extract_text() returns None (not an empty string) when a
            # page has no recoverable text -- e.g. a scanned image with
            # no character data at all. `or ""` keeps everything downstream
            # working with plain strings instead of crashing on None.
            text = page.extract_text() or ""
            pages_text.append(f"--- Page {page_number} ---\n{text}")
    return "\n\n".join(pages_text)


def process_file(pdf_path: Path, output_dir: Path | None) -> None:
    """Extract one PDF's text and either print it or save it to a .txt file."""
    text = extract_text(pdf_path)

    if not text.strip():
        # A digital-native PDF should never end up here. If it does, the
        # PDF is probably a scanned image -- see Chapter 6 for OCR.
        print(f"[warning] No extractable text in {pdf_path.name} "
              f"— it may be a scanned image. See Chapter 6 for OCR.", file=sys.stderr)

    if output_dir is None:
        print(f"===== {pdf_path.name} =====")
        print(text)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Same filename, .txt instead of .pdf, so it's easy to match a
        # report back to its source PDF later.
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
        # --batch processes every PDF in a folder in one run, instead of
        # calling this script once per file by hand.
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
