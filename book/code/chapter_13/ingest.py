"""Chapter 13: incremental daily ingestion.

Everything before this chapter processes a fixed archive in one batch. But
these are *Daily* Drilling Reports: in a real deployment one new report
arrives every day, and the system has to absorb it without rebuilding
from scratch. This module does exactly that -- ingest one new report PDF
into a live, persisted index, incrementally -- and re-runs the gap check.

It reuses the book's own code end to end and adds only the orchestration:
  extract (Ch 1) -> quality gate (Ch 6) -> chunk (Ch 7) -> embed (Ch 4)
  -> append to the FAISS index (Ch 8) -> re-check reporting gaps (Ch 10).

Two things make this "incremental", not "rebuild":
  - The dense index is append-only: faiss.IndexFlatIP.add() bolts the new
    chunks onto the existing index; nothing is re-embedded.
  - Because an append-only index can't easily un-add a row, ingestion
    checks up front and skips any report already in the index.

Usage:
    # ingest one report
    python code/chapter_13/ingest.py datasets/sample_ddrs/FORGE-16A-78-32_Drilling_050_2020-12-08.pdf
    # or catch up on every report not yet ingested
    python code/chapter_13/ingest.py
"""

import os

# Must be set before faiss or torch is imported anywhere -- see Chapter 8
# for the libomp crash this avoids.
os.environ.setdefault("OMP_NUM_THREADS", "1")

import json
import sys
from pathlib import Path

import faiss
import numpy as np

_CODE = Path(__file__).resolve().parents[1]
for _chapter in ("chapter_01", "chapter_04", "chapter_06", "chapter_07", "chapter_08", "chapter_10"):
    sys.path.insert(0, str(_CODE / _chapter))

from read_ddr import extract_text                       # Ch 1  # noqa: E402
from semantic_search import MODEL_NAME, embed_texts     # Ch 4  # noqa: E402
from sentence_transformers import SentenceTransformer   # noqa: E402
from ocr_quality_gate import evaluate_ocr_quality       # Ch 6  # noqa: E402
from token_chunking import chunk_pages_by_tokens        # Ch 7  # noqa: E402
from build_faiss_index import load_index, report_date, save_index, search  # Ch 8  # noqa: E402
from traceable_answers import find_date_gaps            # Ch 10  # noqa: E402

INDEX_PATH = Path("datasets/ddr_live.index")
META_PATH = Path("datasets/ddr_live_meta.json")


def load_state(index_path: Path = INDEX_PATH, meta_path: Path = META_PATH):
    """Load the live index and its parallel chunk-metadata list, or empty
    state on first run."""
    if index_path.exists() and meta_path.exists():
        return load_index(index_path), json.loads(meta_path.read_text(encoding="utf-8"))
    return None, []


def save_state(index, metadata, index_path: Path = INDEX_PATH, meta_path: Path = META_PATH):
    save_index(index, index_path)
    meta_path.write_text(json.dumps(metadata), encoding="utf-8")


def already_ingested(metadata: list[dict], report: str) -> bool:
    return any(record["report"] == report for record in metadata)


def ingest_report(pdf_path: Path, model, index, metadata: list[dict]):
    """Ingest one report PDF into the live index, incrementally.

    Returns (index, chunks_added, status). A report already in the index
    is skipped; a report the quality gate rejects is not indexed.
    """
    report = pdf_path.name
    if already_ingested(metadata, report):
        return index, 0, "skipped (already ingested)"

    text = extract_text(pdf_path)
    gate = evaluate_ocr_quality(text)
    if gate["reject_ocr"]:
        return index, 0, f"rejected by quality gate: {gate['flags']}"

    date = report_date(report)
    pairs = chunk_pages_by_tokens(text, chunk_tokens=60, overlap_tokens=15)
    vectors = embed_texts(model, [chunk for _page, chunk in pairs]).astype("float32")

    if index is None:
        index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)  # <-- the whole point: append, don't rebuild
    for page, _chunk in pairs:
        metadata.append({"report": report, "page": page, "date": date})

    return index, len(pairs), "ingested"


def ingested_dates(metadata: list[dict]) -> list[str]:
    return sorted({record["date"] for record in metadata if record.get("date")})


if __name__ == "__main__":
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    index, metadata = load_state()

    incoming = [Path(a) for a in sys.argv[1:]] or sorted(Path("datasets/sample_ddrs").glob("*.pdf"))
    for pdf in incoming:
        index, added, status = ingest_report(pdf, model, index, metadata)
        print(f"{pdf.name}: {status}" + (f" (+{added} chunks)" if added else ""))

    save_state(index, metadata)
    reports = len({record["report"] for record in metadata})
    print(f"\nLive index: {index.ntotal} chunks across {reports} reports")
    gaps = find_date_gaps(ingested_dates(metadata))
    print(f"Reporting gaps now: {gaps or 'none'}")
