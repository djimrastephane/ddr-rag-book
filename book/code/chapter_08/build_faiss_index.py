"""Chapter 8: build a FAISS IndexFlatIP over DDR chunk embeddings.

Usage:
    python code/chapter_08/build_faiss_index.py
"""

import sys
from pathlib import Path

import faiss
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_04"))
from semantic_search import MODEL_NAME, embed_texts, load_chunks  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402


def build_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """IndexFlatIP does an exact inner-product search -- no approximation.
    Because Chapter 4's embeddings are normalized to length 1, inner
    product and cosine similarity are the same computation, so this index
    finds exactly the same nearest neighbours as Chapter 4's brute-force
    NumPy search, just via FAISS's much faster C++ implementation.
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype("float32"))
    return index


def save_index(index: faiss.Index, path: Path) -> None:
    """Write the index to disk so it doesn't have to be rebuilt from
    scratch every time you want to search it."""
    faiss.write_index(index, str(path))


def load_index(path: Path) -> faiss.Index:
    return faiss.read_index(str(path))


def search(index: faiss.Index, query_vec: np.ndarray, top_k: int = 5):
    """FAISS wants a 2D array even for a single query, hence reshape(1, -1).
    Returns (row index into the original embeddings, similarity score)
    pairs -- the row index is what you use to look up the filename."""
    scores, indices = index.search(query_vec.reshape(1, -1).astype("float32"), top_k)
    return list(zip(indices[0].tolist(), scores[0].tolist()))


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 1's batch extraction first.")

    # device="cpu" pinned explicitly -- see code/chapter_04/semantic_search.py
    # for why: Apple Silicon otherwise auto-selects the MPS backend, which
    # produces meaningfully different embeddings than CPU.
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    filenames, texts = load_chunks(text_dir)
    embeddings = embed_texts(model, texts)

    index = build_index(embeddings)
    index_path = Path("datasets/sample_ddrs.index")
    save_index(index, index_path)
    print(f"Built and saved FAISS index: {len(filenames)} vectors, {embeddings.shape[1]}d -> {index_path}")

    reloaded = load_index(index_path)
    query_vec = model.encode(["stuck pipe"], normalize_embeddings=True)[0]
    results = search(reloaded, query_vec, top_k=5)
    print("\nTop 5 for 'stuck pipe' (reloaded index):")
    for idx, score in results:
        print(f"  {score:.4f}  {filenames[idx]}")
