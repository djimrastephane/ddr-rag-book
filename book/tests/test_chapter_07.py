"""Tests for code/chapter_07/token_chunking.py.

The two chunking tests below are marked slow: tiktoken downloads its BPE
vocabulary file on first use. The validation tests are not slow -- they
raise before tiktoken is ever called.
"""

import pytest


def test_chunk_text_by_tokens_rejects_overlap_not_smaller_than_chunk():
    from token_chunking import chunk_text_by_tokens

    with pytest.raises(ValueError, match="overlap_tokens"):
        chunk_text_by_tokens("some report text", chunk_tokens=10, overlap_tokens=10)


def test_chunk_text_by_tokens_rejects_non_positive_chunk_tokens():
    from token_chunking import chunk_text_by_tokens

    with pytest.raises(ValueError, match="chunk_tokens"):
        chunk_text_by_tokens("some report text", chunk_tokens=0, overlap_tokens=0)


def test_chunk_text_by_tokens_rejects_negative_overlap():
    from token_chunking import chunk_text_by_tokens

    with pytest.raises(ValueError, match="overlap_tokens"):
        chunk_text_by_tokens("some report text", chunk_tokens=10, overlap_tokens=-1)


def test_chunk_pages_by_tokens_rejects_text_with_no_page_markers():
    from token_chunking import chunk_pages_by_tokens

    with pytest.raises(ValueError, match="Page"):
        chunk_pages_by_tokens("just some plain text, never run through Chapter 1")


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
