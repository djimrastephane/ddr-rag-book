"""Tests for code/chapter_04/semantic_search.py.

Marked slow: this downloads the all-MiniLM-L6-v2 model on first run.
"""

import pytest


@pytest.fixture(scope="module")
def model():
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


@pytest.mark.slow
def test_search_ranks_report_038_and_039_in_top_five(extracted_sample_text_dir, model):
    from semantic_search import embed_texts, load_chunks, search

    filenames, texts = load_chunks(extracted_sample_text_dir)
    embeddings = embed_texts(model, texts)

    results = search(model, "stuck pipe", filenames, embeddings, top_k=10)
    top_five = [name for name, _score in results[:5]]

    # Matches Chapter 4's own documented ranking: report #38 (the actual
    # incident) at rank 2, report #39 (the day after) at rank 5.
    assert any("038" in name for name in top_five)
    assert any("039" in name for name in top_five)
