"""Tests for code/chapter_07/token_chunking.py.

Marked slow: tiktoken downloads its BPE vocabulary file on first use.
"""

import pytest


@pytest.mark.slow
def test_chunking_keeps_the_stuck_pipe_sentence_whole(report_038_pdf):
    from read_ddr import extract_text
    from token_chunking import chunk_text_by_tokens

    text = extract_text(report_038_pdf)
    chunks = chunk_text_by_tokens(text, chunk_tokens=60, overlap_tokens=15)

    assert len(chunks) > 1
    assert any("became stuck" in chunk for chunk in chunks)


@pytest.mark.slow
def test_chunk_pages_by_tokens_attaches_the_real_page_number(report_038_pdf):
    from read_ddr import extract_text
    from token_chunking import chunk_pages_by_tokens

    text = extract_text(report_038_pdf)
    chunks_with_pages = chunk_pages_by_tokens(text, chunk_tokens=60, overlap_tokens=15)

    assert len(chunks_with_pages) > 1
    # Report #38 is a single-page DDR, so every chunk must trace back to page 1.
    assert all(page == 1 for page, _chunk in chunks_with_pages)
    assert any("became stuck" in chunk for _page, chunk in chunks_with_pages)
