"""Tests for code/chapter_10/traceable_answers.py."""

import pytest


def test_citations_from_search_reads_the_real_metadata_not_the_score():
    from traceable_answers import Citation, citations_from_search

    metadata = [
        {"report": "report_038.pdf", "page": 1, "date": "2020-11-26"},
        {"report": "report_039.pdf", "page": 1, "date": "2020-11-27"},
    ]
    chunk_results = [(1, 0.42), (0, 0.31)]  # (row index, score) -- index order, not row 0..n

    citations = citations_from_search(chunk_results, metadata)

    assert citations == [
        Citation(report="report_039.pdf", page=1, report_date="2020-11-27"),
        Citation(report="report_038.pdf", page=1, report_date="2020-11-26"),
    ]


def test_citations_from_search_dedupes_repeated_report_page_pairs():
    from traceable_answers import Citation, citations_from_search

    # Two chunks from the same report/page (idx 0 and idx 2) plus one
    # from a different page -- the same shape a long page's multiple
    # chunks can produce among a real top-k result.
    metadata = [
        {"report": "report_038.pdf", "page": 1, "date": "2020-11-26"},
        {"report": "report_039.pdf", "page": 1, "date": "2020-11-27"},
        {"report": "report_038.pdf", "page": 1, "date": "2020-11-26"},
    ]
    chunk_results = [(0, 0.42), (1, 0.35), (2, 0.31)]  # idx 2 duplicates idx 0's (report, page)

    citations = citations_from_search(chunk_results, metadata)

    # The best-ranked (first) occurrence of the duplicate is kept, and
    # order among the remaining, distinct citations is preserved.
    assert citations == [
        Citation(report="report_038.pdf", page=1, report_date="2020-11-26"),
        Citation(report="report_039.pdf", page=1, report_date="2020-11-27"),
    ]


def test_citations_from_search_tolerates_metadata_without_a_date():
    from traceable_answers import Citation, citations_from_search

    metadata = [{"report": "report_038.pdf", "page": 1}]  # no "date" key at all

    citations = citations_from_search([(0, 0.5)], metadata)

    assert citations == [Citation(report="report_038.pdf", page=1, report_date=None)]


@pytest.mark.slow
def test_citations_from_search_cites_the_real_stuck_pipe_page(extracted_sample_text_dir):
    from build_faiss_index import build_chunk_metadata_index, search
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer
    from traceable_answers import citations_from_search, format_evidence

    model = SentenceTransformer(MODEL_NAME, device="cpu")
    index, metadata = build_chunk_metadata_index(extracted_sample_text_dir, model)
    query_vec = model.encode(["stuck pipe"], normalize_embeddings=True)[0]
    results = search(index, query_vec, top_k=1)

    citations = citations_from_search(results, metadata)
    evidence = format_evidence(citations)

    assert "FORGE-16A-78-32_Drilling_038_2020-11-26.txt page 1 (2020-11-26)" in evidence


@pytest.mark.slow
def test_citations_from_search_dedupes_the_real_top_k_results(extracted_sample_text_dir):
    from build_faiss_index import build_chunk_metadata_index, search
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer
    from traceable_answers import citations_from_search

    model = SentenceTransformer(MODEL_NAME, device="cpu")
    index, metadata = build_chunk_metadata_index(extracted_sample_text_dir, model)
    query_vec = model.encode(["stuck pipe"], normalize_embeddings=True)[0]
    results = search(index, query_vec, top_k=10)

    citations = citations_from_search(results, metadata)

    # 10 chunk results come back, but this archive's real repeated pages
    # collapse them to fewer distinct (report, page) citations -- never
    # more citations than results, and no duplicate (report, page) pairs.
    assert len(citations) < len(results)
    seen = [(c.report, c.page) for c in citations]
    assert len(seen) == len(set(seen))


def test_format_evidence_lists_report_and_page():
    from traceable_answers import Citation, format_evidence

    evidence = format_evidence([Citation(report="report_038.pdf", page=1)])

    assert "report_038.pdf page 1" in evidence


def test_format_evidence_includes_the_report_date_when_present():
    from traceable_answers import Citation, format_evidence

    evidence = format_evidence([Citation(report="report_038.pdf", page=1, report_date="2020-11-26")])

    assert "report_038.pdf page 1 (2020-11-26)" in evidence


def test_find_date_gaps_detects_the_real_archive_gaps():
    from traceable_answers import find_date_gaps

    sample_dates = [
        "2020-10-22", "2020-11-07", "2020-11-24", "2020-11-25",
        "2020-11-26", "2020-11-27", "2020-12-06", "2020-12-07",
        "2020-12-08", "2021-01-06",
    ]
    gaps = find_date_gaps(sample_dates)

    assert len(gaps) == 4
    # The real gap right before the Completion report, discussed in Ch.10.
    assert gaps[-1] == ("2020-12-09", "2021-01-05")
