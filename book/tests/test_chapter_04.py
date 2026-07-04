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
def test_search_ranks_report_038_above_039_above_an_unrelated_report(extracted_sample_text_dir, model):
    from semantic_search import embed_texts, load_chunks, search

    filenames, texts = load_chunks(extracted_sample_text_dir)
    embeddings = embed_texts(model, texts)

    results = search(model, "stuck pipe", filenames, embeddings, top_k=len(filenames))
    scores = dict(results)

    report_038 = next(name for name in scores if "038" in name)
    report_039 = next(name for name in scores if "039" in name)
    report_036 = next(name for name in scores if "036" in name)  # genuinely unrelated coring day

    # Matches Chapter 4's own documented result: report #38 (the actual
    # incident) scores clearly highest, and report #39 (the day after,
    # still showing continued-risk language) scores clearly above a
    # genuinely unrelated report. Several of this book's ten sample
    # reports score closely together (Chapter 4's own Field Notes call
    # this out directly), so an exact top-5 cutoff can flip by one rank
    # between BLAS backends on different platforms even with identical
    # code and pinned dependency versions -- these two comfortable-margin
    # relationships are the actual, robust claim being tested.
    assert scores[report_038] > scores[report_039]
    assert scores[report_039] > scores[report_036]
