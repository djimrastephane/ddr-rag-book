"""Chapter 11 challenge solution: a 15-question evaluation set against the
full 76-report archive, with recall@5 computed for real.

Every question below was found by hand, by scanning the real archive for
distinctive real events -- the same discipline the chapter's practical
exercise used for its five-question starter set, just scaled up. This is
genuinely new evaluation data: as far as this book's companion pipeline
is concerned, this is the first real question set built against the
Utah FORGE archive.

Usage:
    python code/chapter_11/challenge/full_archive_eval.py
"""

import sys
from pathlib import Path

import numpy as np
import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "chapter_04"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semantic_search import MODEL_NAME  # noqa: E402
from eval_metrics import recall_at_k, mrr, ndcg_at_k  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

ARCHIVE_DIR = Path("datasets/forge_archive")

# (question, expected report filename) -- each one verified by hand
# against the real report text before being added here.
QUESTIONS = [
    ("Which report describes the drill pipe becoming stuck during a slide?",
     "FORGE-16A-78-32_Drilling_038_2020-11-26.pdf"),
    ("Which report shows packers failing to set?",
     "FORGE-16A-78-32_Drilling_049_2020-12-07.pdf"),
    ("Which report describes milling up lost pieces of bit?",
     "FORGE-16A-78-32_Drilling_050_2020-12-08.pdf"),
    ("Which report mentions mud fluid seepage losses?",
     "FORGE-16A-78-32_Drilling_019_2020-11-07.pdf"),
    ("Which report shows the crew rigging up before spud?",
     "FORGE-16A-78-32_Drilling_003_2020-10-22.pdf"),
    ("Which report describes a wash out that damaged a module beyond repair?",
     "FORGE-16A-78-32_Drilling_023_2020-11-11.pdf"),
    ("Which report first mentions preparing for extended leak-off tests?",
     "FORGE-16A-78-32_Drilling_044_2020-12-02.pdf"),
    ("Which report describes drilling out cement and formation to test the casing shoe?",
     "FORGE-16A-78-32_Drilling_011_2020-10-30.pdf"),
    ("Which report mentions bit junk packed off with red clay?",
     "FORGE-16A-78-32_Drilling_020_2020-11-08.pdf"),
    ("Which report shows the crew tripping out of hole for a washout on the drill string?",
     "FORGE-16A-78-32_Drilling_051_2020-12-09.pdf"),
    ("Which report describes high torque leading to a decision to pull out of hole?",
     "FORGE-16A-78-32_Drilling_039_2020-11-27.pdf"),
    ("Which report shows a sharp ROP decrease?",
     "FORGE-16A-78-32_Drilling_048_2020-12-06.pdf"),
    ("Which report describes rigging up Schlumberger to prepare for logging?",
     "FORGE-16A-78-32_Drilling_037_2020-11-25.pdf"),
    ("Which report describes a coring operation with wireline string shots?",
     "FORGE-16A-78-32_Drilling_036_2020-11-24.pdf"),
    ("Which report is the diagnostic fracture injection test (DFIT)?",
     "FORGE-16A-78-32_Completion_003_2021-01-06.pdf"),
]


def extract_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n\n".join((page.extract_text() or "") for page in pdf.pages)


if __name__ == "__main__":
    if not ARCHIVE_DIR.exists():
        raise SystemExit(f"{ARCHIVE_DIR} does not exist -- see Appendix A for how to obtain it.")

    pdf_files = sorted(ARCHIVE_DIR.glob("*.pdf"))
    filenames = [p.name for p in pdf_files]
    texts = [extract_text(p) for p in pdf_files]

    print(f"Embedding {len(filenames)} reports (this takes a moment)...")
    # device="cpu" pinned explicitly -- see code/chapter_04/semantic_search.py
    # for why: Apple Silicon otherwise auto-selects the MPS backend, which
    # produces meaningfully different embeddings than CPU.
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    embeddings = model.encode(texts, normalize_embeddings=True)

    results = []
    for question, expected_file in QUESTIONS:
        query_vec = model.encode([question], normalize_embeddings=True)[0]
        scores = embeddings @ query_vec
        order = np.argsort(-scores)
        ranked_names = [filenames[i] for i in order]
        rank = ranked_names.index(expected_file) + 1 if expected_file in ranked_names else None
        results.append({"question": question, "rank": rank})
        print(f"  rank {rank!s:>4}  {question[:70]}")

    print(f"\nrecall@5: {recall_at_k(results, k=5):.2f}")
    print(f"MRR:      {mrr(results):.2f}")
    print(f"NDCG@5:   {ndcg_at_k(results, k=5):.2f}")
