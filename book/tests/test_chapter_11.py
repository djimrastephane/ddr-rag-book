"""Tests for code/chapter_11/eval_metrics.py."""

import pytest


def test_recall_mrr_ndcg_match_the_chapters_worked_example():
    from eval_metrics import mrr, ndcg_at_k, recall_at_k

    sample_results = [
        {"question": "Q1", "rank": 1},
        {"question": "Q2", "rank": 1},
        {"question": "Q3", "rank": 2},
        {"question": "Q4", "rank": 1},
        {"question": "Q5", "rank": None},
    ]

    assert recall_at_k(sample_results, k=3) == pytest.approx(0.8)
    assert mrr(sample_results) == pytest.approx(0.7)
    assert ndcg_at_k(sample_results, k=3) == pytest.approx(0.7261859507142916)


def test_mrr_and_ndcg_reject_rank_zero_instead_of_treating_it_as_a_miss():
    """Ranks are 1-indexed throughout this book -- a `rank` of 0 is
    invalid input, not a valid "found at position 0" hit. Before the
    `is not None` fix, a falsy check (`if r.get("rank")`) would have
    silently treated rank 0 the same as rank None (not found), scoring
    it as 0.0 with no warning. Now it surfaces immediately as a
    ZeroDivisionError instead of a silently wrong score.
    """
    from eval_metrics import mrr, ndcg_at_k

    invalid_result = [{"question": "Q1", "rank": 0}]

    with pytest.raises(ZeroDivisionError):
        mrr(invalid_result)

    with pytest.raises(ZeroDivisionError):
        ndcg_at_k(invalid_result, k=3)
