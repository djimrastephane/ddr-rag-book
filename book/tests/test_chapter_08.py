"""Tests for code/chapter_08/build_faiss_index.py.

Marked slow: builds real sentence embeddings before indexing them.
"""

import numpy as np
import pytest


def test_report_date_reads_the_real_filename_convention():
    from build_faiss_index import report_date

    assert report_date("FORGE-16A-78-32_Drilling_038_2020-11-26.txt") == "2020-11-26"
    assert report_date("FORGE-16A-78-32_Completion_003_2021-01-06.pdf") == "2021-01-06"
    assert report_date("no_date_here.txt") is None


@pytest.mark.slow
def test_faiss_index_matches_brute_force_search(extracted_sample_text_dir, tmp_path):
    from build_faiss_index import build_index, load_index, save_index, search
    from semantic_search import MODEL_NAME, embed_texts, load_chunks
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME, device="cpu")
    filenames, texts = load_chunks(extracted_sample_text_dir)
    embeddings = embed_texts(model, texts)

    index = build_index(embeddings)
    index_path = tmp_path / "sample.index"
    save_index(index, index_path)
    reloaded = load_index(index_path)

    query_vec = model.encode(["stuck pipe"], normalize_embeddings=True)[0]
    brute_order = [filenames[i] for i in np.argsort(-(embeddings @ query_vec))]
    faiss_order = [
        filenames[i]
        for i, _score in search(reloaded, query_vec, top_k=len(filenames))
    ]

    # IndexFlatIP is exact, not approximate, so it must agree with
    # brute-force NumPy search on every rank, not just the top result.
    assert faiss_order == brute_order


@pytest.mark.slow
def test_chunk_metadata_index_cites_the_real_stuck_pipe_page(extracted_sample_text_dir):
    from build_faiss_index import build_chunk_metadata_index, search
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME, device="cpu")
    index, metadata = build_chunk_metadata_index(extracted_sample_text_dir, model)

    # One metadata record per indexed chunk, not per report.
    assert len(metadata) == index.ntotal
    assert len(metadata) > 10  # more chunks than reports in the sample archive

    query_vec = model.encode(["stuck pipe"], normalize_embeddings=True)[0]
    results = search(index, query_vec, top_k=3)
    top = metadata[results[0][0]]

    assert top["report"] == "FORGE-16A-78-32_Drilling_038_2020-11-26.txt"
    assert top["page"] == 1
    assert top["date"] == "2020-11-26"
