"""Chapter 4: semantic search over DDR text using sentence embeddings.

Usage:
    python code/chapter_04/semantic_search.py "stuck pipe"
"""

import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

# A small, fast embedding model -- good enough to prove the concept and
# light enough to run on a laptop CPU with no GPU required.
MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks(text_dir: Path) -> tuple[list[str], list[str]]:
    """Load every .txt file in a folder as one big chunk of text each.

    "Chunk" here means "whole document" -- Chapter 4 embeds each entire
    report as a single vector. Chapter 7 revisits this with much smaller
    chunks, once the granularity problem this causes becomes clear.
    """
    filenames, texts = [], []
    for path in sorted(text_dir.glob("*.txt")):
        filenames.append(path.name)
        texts.append(path.read_text(encoding="utf-8"))
    return filenames, texts


def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    """Turn a list of strings into a matrix of embedding vectors.

    normalize_embeddings=True rescales every vector to length 1. That's
    what makes the plain dot product in search() below equivalent to
    cosine similarity -- no separate normalization step needed later.
    """
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.asarray(embeddings)


def search(model: SentenceTransformer, query: str, filenames: list[str],
           embeddings: np.ndarray, top_k: int = 3) -> list[tuple[str, float]]:
    """Embed the query, score it against every document, return the top k.

    `embeddings @ query_vec` is a single matrix-vector multiply that
    computes the cosine similarity between the query and every document
    at once -- one number per document, higher meaning "more similar."
    `np.argsort(-scores)` sorts descending (argsort is ascending by
    default, so negating the scores flips the order) and `[:top_k]` keeps
    only the best matches.
    """
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    scores = embeddings @ query_vec  # cosine similarity, since vectors are normalized
    top_indices = np.argsort(-scores)[:top_k]
    return [(filenames[i], float(scores[i])) for i in top_indices]


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 1's batch extraction first.")

    query = " ".join(sys.argv[1:]) or "stuck pipe"
    model = SentenceTransformer(MODEL_NAME)
    filenames, texts = load_chunks(text_dir)
    embeddings = embed_texts(model, texts)

    results = search(model, query, filenames, embeddings, top_k=len(filenames))
    print(f"Query: {query!r}")
    for rank, (name, score) in enumerate(results, start=1):
        print(f"{rank}. {score:.4f}  {name}")
