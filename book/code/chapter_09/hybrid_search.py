"""Chapter 9: combine ranked lists from different retrieval methods with
Reciprocal Rank Fusion (RRF).

Usage:
    python code/chapter_09/hybrid_search.py
"""

from collections import defaultdict


def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 20,
                            weights: list[float] | None = None) -> list[tuple[str, float]]:
    """Combine several ranked lists of document IDs into one fused ranking.

    Each list contributes `weight / (k + rank)` to a document's fused
    score -- so being ranked #1 in a list is worth much more than being
    ranked #10, but the raw magnitude of any one method's scores never
    enters the calculation. That's the key idea: RRF fuses by *rank*, not
    by raw score, which sidesteps the problem of BM25 and cosine
    similarity living on completely different, incomparable scales.

    `k` softens the curve -- a larger k means the difference between
    rank 1 and rank 2 matters less. `weights` lets one retrieval method
    count for more than another in the fused result.
    """
    weights = weights or [1.0] * len(ranked_lists)
    scores: dict[str, float] = defaultdict(float)
    for ranked_list, weight in zip(ranked_lists, weights):
        for rank, doc_id in enumerate(ranked_list, start=1):
            scores[doc_id] += weight * (1.0 / (k + rank))
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


if __name__ == "__main__":
    # A small worked example: two retrieval methods disagree on ordering,
    # and RRF blends their opinions into one ranking.
    bm25_ranked = ["report_049", "report_038", "report_003"]
    dense_ranked = ["report_038", "report_049", "report_050"]

    fused = reciprocal_rank_fusion(
        [bm25_ranked, dense_ranked],
        k=20,
        weights=[2.0, 0.5],  # matches the companion pipeline's real BM25/dense weighting
    )
    print("Fused ranking (BM25 weight 2.0, dense weight 0.5):")
    for doc_id, score in fused:
        print(f"  {score:.5f}  {doc_id}")
