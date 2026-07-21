"""Tests for code/chapter_13/ingest.py -- incremental daily ingestion.

conftest.py adds every code/chapter_NN folder to sys.path (now through
13), so `import ingest` resolves. The slow tests load the embedding model.
"""

from pathlib import Path

import pytest


def test_helpers_track_ingested_reports_and_dates():
    import ingest

    metadata = [
        {"report": "a.pdf", "page": 1, "date": "2020-01-01"},
        {"report": "a.pdf", "page": 1, "date": "2020-01-01"},
        {"report": "b.pdf", "page": 2, "date": "2020-01-03"},
    ]
    assert ingest.already_ingested(metadata, "a.pdf")
    assert not ingest.already_ingested(metadata, "c.pdf")
    assert ingest.ingested_dates(metadata) == ["2020-01-01", "2020-01-03"]


def test_ingest_report_raises_a_readable_error_for_a_missing_pdf():
    import ingest

    missing = Path("datasets/sample_ddrs/does_not_exist_038.pdf")
    with pytest.raises(FileNotFoundError, match="does not exist"):
        ingest.ingest_report(missing, model=None, index=None, metadata=[])


def test_require_index_raises_when_nothing_was_ingested():
    import ingest

    with pytest.raises(SystemExit, match="Nothing was ingested"):
        ingest.require_index(None)


def test_require_index_passes_when_an_index_already_exists():
    import ingest

    ingest.require_index(object())  # any non-None value means "don't raise"


@pytest.fixture(scope="module")
def model():
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, device="cpu")


@pytest.mark.slow
def test_ingest_appends_is_searchable_and_skips_duplicates(model, sample_ddrs_dir):
    import ingest
    from build_faiss_index import search

    pdfs = sorted(sample_ddrs_dir.glob("*.pdf"))
    new_report = next(p for p in pdfs if "Drilling_050" in p.name)
    first_nine = [p for p in pdfs if "Drilling_050" not in p.name]

    index, metadata = None, []
    for pdf in first_nine:
        index, _added, _status = ingest.ingest_report(pdf, model, index, metadata)
    before = index.ntotal

    # A new report appends -- the index grows by exactly its chunk count.
    index, added, status = ingest.ingest_report(new_report, model, index, metadata)
    assert status == "ingested" and added > 0
    assert index.ntotal == before + added
    assert ingest.already_ingested(metadata, new_report.name)

    # ...and its appended rows are immediately retrievable.
    query_vec = model.encode(
        ["fishing milled up lost pieces of bit"], normalize_embeddings=True)[0]
    top = [metadata[i]["report"] for i, _score in search(index, query_vec, top_k=3)]
    assert any("050" in name for name in top)

    # Skip duplicates: re-ingesting the same report is a no-op.
    index, added_again, status_again = ingest.ingest_report(new_report, model, index, metadata)
    assert added_again == 0
    assert status_again.startswith("skipped")
    assert index.ntotal == before + added


@pytest.mark.slow
def test_incremental_ingestion_matches_the_batch_chunk_count(model, sample_ddrs_dir):
    # Ingesting the ten sample reports one at a time yields the same 333
    # chunks Chapter 8's one-shot build produces -- incremental == batch.
    import ingest

    index, metadata = None, []
    for pdf in sorted(sample_ddrs_dir.glob("*.pdf")):
        index, _added, _status = ingest.ingest_report(pdf, model, index, metadata)

    assert index.ntotal == 333
    assert len({m["report"] for m in metadata}) == 10
