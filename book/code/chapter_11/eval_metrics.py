"""Chapter 11: retrieval evaluation metrics -- recall@k, MRR, NDCG@k.

Usage:
    python code/chapter_11/eval_metrics.py
"""

import math


def recall_at_k(results: list[dict], k: int) -> float:
    """Fraction of questions where the correct report appeared anywhere
    in the top k retrieved results. `rank` is None if it wasn't found at
    all within whatever top-k window the retrieval step considered."""
    hits = [r for r in results if r.get("rank") is not None and r["rank"] <= k]
    return len(hits) / len(results) if results else 0.0


def mrr(results: list[dict]) -> float:
    """Mean Reciprocal Rank: average of 1/rank across all questions.
    A correct answer at rank 1 scores 1.0; at rank 10 it scores only 0.1.
    This rewards ranking the right answer FIRST, not just somewhere in
    the results -- closer to what a user actually experiences than
    recall@k alone.
    """
    scores = [1.0 / r["rank"] if r.get("rank") else 0.0 for r in results]
    return sum(scores) / len(scores) if scores else 0.0


def ndcg_at_k(results: list[dict], k: int) -> float:
    """Normalized Discounted Cumulative Gain: like recall@k, but a hit at
    rank 1 counts for more than a hit at rank k -- log2(rank + 1) grows
    slowly, so the "discount" for being ranked lower is gentle at first
    and steeper further down.
    """
    scores = []
    for r in results:
        rank = r.get("rank")
        scores.append(1.0 / math.log2(rank + 1) if rank and rank <= k else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


if __name__ == "__main__":
    # A small worked example: five questions, with the rank at which each
    # one's correct report was actually retrieved (None = not found).
    sample_results = [
        {"question": "Q1", "rank": 1},
        {"question": "Q2", "rank": 1},
        {"question": "Q3", "rank": 2},
        {"question": "Q4", "rank": 1},
        {"question": "Q5", "rank": None},
    ]
    print(f"recall@3: {recall_at_k(sample_results, k=3):.2f}")
    print(f"MRR:      {mrr(sample_results):.2f}")
    print(f"NDCG@3:   {ndcg_at_k(sample_results, k=3):.2f}")
