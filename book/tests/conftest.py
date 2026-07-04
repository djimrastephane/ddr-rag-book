"""Shared fixtures for the book's code tests.

Every chapter's script in code/chapter_NN/ is written as a standalone
file, not a package -- readers run them directly with `python
code/chapter_NN/script.py`. To test the real functions inside them
without duplicating any code, each chapter's folder is added to
sys.path here, so tests can just `import read_ddr`, `import
expand_abbreviations`, and so on, exactly as if that file were the only
thing on the path -- which mirrors how a reader actually runs them.
"""

import sys
from pathlib import Path

import pytest

BOOK_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DDRS_DIR = BOOK_ROOT / "datasets" / "sample_ddrs"

for _n in range(1, 13):
    _chapter_dir = BOOK_ROOT / "code" / f"chapter_{_n:02d}"
    if _chapter_dir.is_dir() and str(_chapter_dir) not in sys.path:
        sys.path.insert(0, str(_chapter_dir))


@pytest.fixture(scope="session")
def sample_ddrs_dir() -> Path:
    return SAMPLE_DDRS_DIR


@pytest.fixture(scope="session")
def report_038_pdf() -> Path:
    """Report #38, 2020-11-26 -- the real stuck-pipe day used throughout
    this book's examples."""
    return SAMPLE_DDRS_DIR / "FORGE-16A-78-32_Drilling_038_2020-11-26.pdf"


@pytest.fixture(scope="session")
def extracted_sample_text_dir(tmp_path_factory) -> Path:
    """Chapter 1's extract_text() run once over all ten sample DDR PDFs.

    Later chapters' tests (search, embeddings, chunking, indexing) build
    on this same real extracted text instead of each re-deriving it, the
    same way the book's own chapters build on Chapter 1's output.
    """
    import read_ddr

    out_dir = tmp_path_factory.mktemp("ddr_text")
    for pdf_path in sorted(SAMPLE_DDRS_DIR.glob("*.pdf")):
        text = read_ddr.extract_text(pdf_path)
        (out_dir / (pdf_path.stem + ".txt")).write_text(text, encoding="utf-8")
    return out_dir
