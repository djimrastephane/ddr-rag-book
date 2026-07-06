"""Chapter 8 challenge solution: chunk and embed the full 76-report
archive, using the companion pipeline's own chunking parameters (224
tokens, 56-token overlap), and see how far a from-scratch pipeline lands
from the companion pipeline's real count of 1,428 chunks.

This deliberately reuses Chapter 1's extraction, Chapter 7's token
chunker, and Chapter 4's embedding model -- the whole point of the
challenge is to see what YOUR version of the pipeline, built chapter by
chapter, produces at real scale, not to match the production number
exactly. Expect a real gap here, not just rounding noise: this book's
`pdfplumber`-based extraction pulls noticeably less text out of each
DDR's data tables than the companion pipeline's table-aware extraction
does, so even with identical chunking parameters this script lands well
under the real count.

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

    # Same chunk size and overlap as the companion pipeline (224/56) --
    # any remaining gap from here is down to extraction completeness,
    # not a difference in chunking parameters.
    pdf_files = sorted(ARCHIVE_DIR.glob("*.pdf"))
    total_chunks = 0
    for pdf_path in pdf_files:
        text = extract_text(pdf_path)
        chunks = chunk_text_by_tokens(text, chunk_tokens=224, overlap_tokens=56)
        total_chunks += len(chunks)

    avg_per_report = total_chunks / len(pdf_files)
    real_count = 1428
    print(f"Chunked {len(pdf_files)} reports into {total_chunks} chunks "
          f"({avg_per_report:.1f} chunks/report on average)")
    print(f"Companion pipeline's real count: {real_count} chunks across 76 reports "
          "(18.8 chunks/report on average)")
    pct_diff = abs(total_chunks - real_count) / real_count * 100
    print(f"Difference from the real count: {pct_diff:.1f}%")
