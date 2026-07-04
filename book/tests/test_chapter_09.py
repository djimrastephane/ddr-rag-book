"""Tests for code/chapter_09/hybrid_search.py."""


def test_reciprocal_rank_fusion_matches_the_pipelines_real_weighting():
    from hybrid_search import reciprocal_rank_fusion

    bm25_ranked = ["report_049", "report_038", "report_003"]
    dense_ranked = ["report_038", "report_049", "report_050"]

    fused = reciprocal_rank_fusion(
        [bm25_ranked, dense_ranked], k=20, weights=[2.0, 0.5]
    )
    fused_order = [doc_id for doc_id, _score in fused]

    assert fused_order == ["report_049", "report_038", "report_003", "report_050"]
