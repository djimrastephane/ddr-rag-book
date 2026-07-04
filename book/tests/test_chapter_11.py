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
