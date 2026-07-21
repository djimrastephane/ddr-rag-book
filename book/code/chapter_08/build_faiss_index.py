"""Chapter 8: build a FAISS IndexFlatIP over DDR chunk embeddings.

Usage:
    python code/chapter_08/build_faiss_index.py
"""

import os

# Must be set before faiss or torch is imported anywhere in this process
# -- avoids a real macOS crash where FAISS's and PyTorch's separate
# OpenMP runtimes collide under multiple threads. See this chapter's
# Production Reality section for the full explanation.
os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
import sys
from pathlib import Path

import faiss
import numpy as np

REPORT_DATE = re.compile(r"_(\d{4}-\d{2}-\d{2})\.")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_04"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_07"))
from semantic_search import MODEL_NAME, embed_texts, load_chunks  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402
from token_chunking import chunk_pages_by_tokens  # noqa: E402


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


def report_date(filename: str) -> str | None:
    """Every report in this archive carries its own date in the filename
    (e.g. "..._2020-11-26.txt") -- WellEz's own naming convention, not
    something this book added. Confirmed against all 76 real filenames in
    the full archive: zero exceptions to the "_YYYY-MM-DD." pattern."""
    match = REPORT_DATE.search(filename)
    return match.group(1) if match else None


def build_chunk_metadata_index(text_dir: Path, model: SentenceTransformer,
                                chunk_tokens: int = 60, overlap_tokens: int = 15
                                ) -> tuple[faiss.Index, list[dict]]:
    """Build an index over real chunks, not whole documents -- and, unlike
    the whole-document demo below, keep a metadata record for every row.

    load_chunks() above (from Chapter 4) treats each whole report as one
    embedding, which is what this chapter's own demo still does. That's a
    real gap: a whole-document row can only ever cite "this report," never
    a page within it. This function closes it by chunking each report with
    Chapter 7's page-aware chunker first, so metadata[i] -- the report
    filename, page number, and report date -- describes exactly what
    embeddings[i] is, row for row.
    """
    metadata: list[dict] = []
    chunk_texts: list[str] = []
    for path in sorted(text_dir.glob("*.txt")):
        pages_text = path.read_text(encoding="utf-8")
        date = report_date(path.name)
        for page_number, chunk in chunk_pages_by_tokens(pages_text, chunk_tokens, overlap_tokens):
            metadata.append({"report": path.name, "page": page_number, "date": date})
            chunk_texts.append(chunk)

    embeddings = embed_texts(model, chunk_texts)
    index = build_index(embeddings)
    return index, metadata


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

    print("\n--- Chunk-level index, with real (report, page, date) metadata ---")
    chunk_index, metadata = build_chunk_metadata_index(text_dir, model)
    print(f"Built chunk index: {len(metadata)} chunks across {len(filenames)} reports")
    chunk_results = search(chunk_index, query_vec, top_k=5)
    print("Top 5 chunks for 'stuck pipe':")
    for idx, score in chunk_results:
        m = metadata[idx]
        print(f"  {score:.4f}  {m['report']} page {m['page']} ({m['date']})")
