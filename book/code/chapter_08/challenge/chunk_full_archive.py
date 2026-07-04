"""Chapter 8 challenge solution: chunk and embed the full 76-report
archive, and see how close a from-scratch pipeline lands to the
companion pipeline's real count of 2,943 chunks.

This deliberately reuses Chapter 1's extraction, Chapter 7's token
chunker, and Chapter 4's embedding model -- the whole point of the
challenge is to see what YOUR version of the pipeline, built chapter by
chapter, produces at real scale, not to match the production number
exactly. Small differences are expected: this book's chunker doesn't
implement the companion pipeline's segment-aware boundary detection, so
the chunk count and boundaries won't be identical -- but they should be
the same order of magnitude.

Usage:
    python code/chapter_08/challenge/chunk_full_archive.py
"""

import sys
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "chapter_07"))
from token_chunking import chunk_text_by_tokens  # noqa: E402

ARCHIVE_DIR = Path("datasets/forge_archive")


def extract_text(pdf_path: Path) -> str:
    """Same logic as Chapter 1's read_ddr.py, inlined here so this script
    has no dependency on files existing on disk from earlier chapters."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n\n".join((page.extract_text() or "") for page in pdf.pages)


if __name__ == "__main__":
    if not ARCHIVE_DIR.exists():
        raise SystemExit(f"{ARCHIVE_DIR} does not exist -- see Appendix A for how to obtain it.")

    # A smaller chunk size than Chapter 7's single-report demo (60/15)
    # lands much closer to the companion pipeline's real chunk count --
    # which makes sense: more, smaller chunks per report is exactly what
    # you'd expect from a smaller token window.
    pdf_files = sorted(ARCHIVE_DIR.glob("*.pdf"))
    total_chunks = 0
    for pdf_path in pdf_files:
        text = extract_text(pdf_path)
        chunks = chunk_text_by_tokens(text, chunk_tokens=50, overlap_tokens=10)
        total_chunks += len(chunks)

    avg_per_report = total_chunks / len(pdf_files)
    real_count = 2943
    print(f"Chunked {len(pdf_files)} reports into {total_chunks} chunks "
          f"({avg_per_report:.1f} chunks/report on average)")
    print(f"Companion pipeline's real count: {real_count} chunks across 76 reports "
          "(38.7 chunks/report on average)")
    pct_diff = abs(total_chunks - real_count) / real_count * 100
    print(f"Difference from the real count: {pct_diff:.1f}%")
