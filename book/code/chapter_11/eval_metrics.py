"""Chapter 11: retrieval evaluation metrics -- recall@k, MRR, NDCG@k.

Usage:
    python code/chapter_11/eval_metrics.py
"""

import math


def _validate_ranks(results: list[dict]) -> None:
    """Enforce this module's one shared contract: every `rank` is either
    `None` (not found) or a 1-indexed integer >= 1. Rank 1 is the best
    possible score, so there's no such thing as rank 0.

    Checked explicitly, up front, in all three metrics below -- rather
    than left to whichever ones happen to divide by `rank` to reject a
    bad value by accident. Dividing would turn an invalid rank of 0 into
    a confusing `ZeroDivisionError`; recall_at_k(), which never divides
    by rank, would otherwise silently count it as a valid hit at the top
    position instead of rejecting it at all. Neither is an acceptable
    way to fail on bad input.
    """
    for r in results:
        rank = r.get("rank")
        if rank is not None and rank < 1:
            raise ValueError(
                f"rank must be None (not found) or an integer >= 1 "
                f"(ranks are 1-indexed), got {rank!r} for {r!r}."
            )


def recall_at_k(results: list[dict], k: int) -> float:
    """Fraction of questions where the correct report appeared anywhere
    in the top k retrieved results. `rank` is None if it wasn't found at
    all within whatever top-k window the retrieval step considered."""
    _validate_ranks(results)
    hits = [r for r in results if r.get("rank") is not None and r["rank"] <= k]
    return len(hits) / len(results) if results else 0.0


def mrr(results: list[dict]) -> float:
    """Mean Reciprocal Rank: average of 1/rank across all questions.
    A correct answer at rank 1 scores 1.0; at rank 10 it scores only 0.1.
    This rewards ranking the right answer FIRST, not just somewhere in
    the results -- closer to what a user actually experiences than
    recall@k alone.

    `rank` must be `None` (not found) or an integer >= 1 -- ranks are
    1-indexed throughout this book, so `r.get("rank") is not None` is
    the correct "was it found" check. A plain truthiness check (`if
    r.get("rank")`) would silently misread a 0-indexed rank of 0 as
    "not found" instead of a hit.
    """
    _validate_ranks(results)
    scores = [1.0 / r["rank"] if r.get("rank") is not None else 0.0 for r in results]
    return sum(scores) / len(scores) if scores else 0.0


def ndcg_at_k(results: list[dict], k: int) -> float:
    """Normalized Discounted Cumulative Gain: like recall@k, but a hit at
    rank 1 counts for more than a hit at rank k -- log2(rank + 1) grows
    slowly, so the "discount" for being ranked lower is gentle at first
    and steeper further down.

    This assumes exactly one relevant document per question, at an ideal
    rank of 1 -- which makes the ideal DCG (IDCG) exactly
    1/log2(1+1) = 1.0, so dividing by it is a no-op and is skipped here.
    Do not reuse this function for an eval set with more than one
    relevant document per question without adding an explicit IDCG term.

    As in mrr() above, `rank` must be `None` or an integer >= 1; the
    "was it found, and within k" check below uses `is not None` rather
    than truthiness for the same reason.
    """
    _validate_ranks(results)
    scores = []
    for r in results:
        rank = r.get("rank")
        found_within_k = rank is not None and rank <= k
        scores.append(1.0 / math.log2(rank + 1) if found_within_k else 0.0)
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
