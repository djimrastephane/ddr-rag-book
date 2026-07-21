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
    if not ranked_lists:
        return []

    if weights is None:
        weights = [1.0] * len(ranked_lists)
    elif len(weights) != len(ranked_lists):
        raise ValueError(
            f"weights has {len(weights)} entries but ranked_lists has "
            f"{len(ranked_lists)} -- pass exactly one weight per ranked list "
            f"(or leave weights=None to weight every list equally). zip() "
            f"would otherwise silently drop whichever lists don't have a "
            f"matching weight."
        )

    scores: dict[str, float] = defaultdict(float)
    for ranked_list, weight in zip(ranked_lists, weights):
        for rank, doc_id in enumerate(ranked_list, start=1):
            scores[doc_id] += weight * (1.0 / (k + rank))
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def hybrid_search(text_dir, model, query: str, k: int = 20,
                  weights: tuple[float, float] = (2.0, 0.5),
                  top_k: int = 10) -> list[tuple[str, float]]:
    """End-to-end hybrid retrieval over a real archive.

    Fuses two genuine ranked lists -- BM25 sparse (this chapter's
    sparse_ranking.py) and Chapter 4's dense semantic search -- with
    Reciprocal Rank Fusion. The default weights (BM25 2.0, dense 0.5)
    match the companion pipeline's real weighting. Imports are kept inside
    the function so reciprocal_rank_fusion above stays importable without
    pulling in sentence-transformers.
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_04"))
    from semantic_search import embed_texts, load_chunks, search  # noqa: E402
    from sparse_ranking import rank_bm25  # noqa: E402

    text_dir = Path(text_dir)
    sparse_ranked = rank_bm25(text_dir, query)

    filenames, texts = load_chunks(text_dir)
    embeddings = embed_texts(model, texts)
    dense_ranked = [name for name, _score
                    in search(model, query, filenames, embeddings, top_k=len(filenames))]

    fused = reciprocal_rank_fusion([sparse_ranked, dense_ranked], k=k, weights=list(weights))
    return fused[:top_k]


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
    print("Fused ranking, toy example (BM25 weight 2.0, dense weight 0.5):")
    for doc_id, score in fused:
        print(f"  {score:.5f}  {doc_id}")

    # The real thing: hybrid retrieval over the ten-report sample archive.
    import sys
    from pathlib import Path

    text_dir = Path("datasets/ddr_text")
    if text_dir.exists():
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_04"))
        # device="cpu" pinned explicitly -- see code/chapter_04/semantic_search.py.
        from semantic_search import MODEL_NAME  # noqa: E402
        from sentence_transformers import SentenceTransformer  # noqa: E402

        model = SentenceTransformer(MODEL_NAME, device="cpu")
        print("\nHybrid ranking for 'packers fishing' over the sample archive:")
        for rank, (name, score) in enumerate(hybrid_search(text_dir, model, "packers fishing"), start=1):
            print(f"  {rank:2d}. {score:.5f}  {name}")
