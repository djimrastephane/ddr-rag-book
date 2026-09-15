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


def test_all_three_metrics_reject_rank_zero_the_same_way():
    """Ranks are 1-indexed throughout this book -- a `rank` of 0 is
    invalid input, not a valid "found at position 0" hit.

    Before this fix, the three metrics disagreed on what to do with it:
    recall_at_k() never divides by rank, so it silently counted 0 as a
    hit at the top position (returning 1.0 instead of rejecting the
    input); mrr() and ndcg_at_k() divide by rank, so they raised a
    confusing ZeroDivisionError instead. Both are wrong ways to handle
    bad input. All three now validate up front and raise the same clear
    ValueError.
    """
    from eval_metrics import mrr, ndcg_at_k, recall_at_k

    invalid_result = [{"question": "Q1", "rank": 0}]

    with pytest.raises(ValueError, match="rank must be"):
        recall_at_k(invalid_result, k=3)

    with pytest.raises(ValueError, match="rank must be"):
        mrr(invalid_result)

    with pytest.raises(ValueError, match="rank must be"):
        ndcg_at_k(invalid_result, k=3)
