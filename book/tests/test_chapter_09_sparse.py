"""Tests for code/chapter_09/sparse_ranking.py and hybrid_search.py.

These cover the gap the book previously had: Chapter 9's exercises asked
readers to fuse a *ranked* sparse list with a dense one, but no ranked
sparse retriever existed (Chapter 3's search() returns an unordered set).
"""

import pytest


def test_rank_bm25_returns_a_full_ranked_list_not_a_set(extracted_sample_text_dir):
    from sparse_ranking import rank_bm25

    ranked = rank_bm25(extracted_sample_text_dir, "packers fishing")

    # A ranked LIST, best-first -- not the unordered set Chapter 3 returns.
    assert isinstance(ranked, list)
    # Every report is ranked, so the fusion step has a position for each.
    assert len(ranked) == 10
    assert len(set(ranked)) == 10  # no duplicates


def test_rank_bm25_puts_the_packers_report_first(extracted_sample_text_dir):
    from sparse_ranking import rank_bm25

    ranked = rank_bm25(extracted_sample_text_dir, "packers fishing")

    # Report #49 is where the packers actually failed to set -- BM25 should
    # rank it first for this query, and the fishing report #50 near the top.
    assert "049" in ranked[0]
    assert any("050" in name for name in ranked[:3])


@pytest.mark.slow
def test_hybrid_search_ranks_packers_and_fishing_reports_at_the_top(extracted_sample_text_dir):
    from hybrid_search import hybrid_search
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME, device="cpu")
    fused = hybrid_search(extracted_sample_text_dir, model, "packers fishing")

    top_two = [name for name, _score in fused[:2]]
    # The exercise's success criterion: both the packers report (#49) and
    # the fishing report (#50) land near the top of the fused ranking.
    assert any("049" in name for name in top_two)
    assert any("050" in name for name in top_two)
