"""Tests for code/chapter_04/semantic_search.py.

Marked slow: this downloads the all-MiniLM-L6-v2 model on first run.

device="cpu" is forced explicitly below. sentence-transformers otherwise
auto-selects Apple's MPS (Metal GPU) backend on Apple Silicon, which
produced meaningfully different -- not just numerically noisy -- scores
than CPU inference in an actual CI run (confirmed by reproducing it:
forcing device="cpu" reproduces this chapter's documented numbers to four
decimal places; leaving the device unset did not, and even reversed the
relative order between two of the book's own worked-example lines).
"""

import pytest


@pytest.fixture(scope="module")
def model():
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, device="cpu")


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


@pytest.mark.slow
def test_line_level_embeddings_clearly_separate_relevant_from_unrelated(model):
    """The reason Chapter 7 moves to line/chunk-level embeddings instead
    of whole documents. These are the same three real lines documented in
    Chapter 4's Field Notes, with the same wide, robust margin (~0.14-0.15)
    that whole-document embeddings can't produce.
    """
    from semantic_search import embed_texts, search

    lines = [
        "Work pipe, circulate lube sweep, work tool back in position, Pipe free",
        "During the slide lost tool face and became assembly became stuck",
        "Trip out of hole with BHA #17 core assembly, lay down core barrels",
    ]
    names = ["report_038_line_a", "report_038_line_b", "report_036_line_unrelated"]

    embeddings = embed_texts(model, lines)
    results = search(model, "stuck pipe", names, embeddings, top_k=3)
    scores = dict(results)

    assert scores["report_038_line_a"] > scores["report_038_line_b"]
    assert scores["report_038_line_b"] > scores["report_036_line_unrelated"]
