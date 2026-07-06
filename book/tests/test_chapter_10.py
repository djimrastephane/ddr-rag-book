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
