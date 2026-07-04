"""Tests for code/chapter_08/build_faiss_index.py.

Marked slow: builds real sentence embeddings before indexing them.
"""

import numpy as np
import pytest


@pytest.mark.slow
def test_faiss_index_matches_brute_force_search(extracted_sample_text_dir, tmp_path):
    from build_faiss_index import build_index, load_index, save_index, search
    from semantic_search import MODEL_NAME, embed_texts, load_chunks
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
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
