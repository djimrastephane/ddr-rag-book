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
