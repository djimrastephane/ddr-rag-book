"""Chapter 10: format citations, and detect gaps in report coverage.

Usage:
    python code/chapter_10/traceable_answers.py
"""

import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass
class Citation:
    report: str
    page: int | None = None
    report_date: str | None = None  # named report_date, not date -- date is
                                     # the stdlib class imported below


def format_evidence(citations: list[Citation]) -> str:
    """Turn a list of citations into a human-readable evidence block --
    the same format used throughout this book's answers, so a claim is
    never presented without a way to check it against the source."""
    lines = []
    for c in citations:
        line = f"  {c.report}"
        if c.page:
            line += f" page {c.page}"
        if c.report_date:
            line += f" ({c.report_date})"
        lines.append(line)
    return "Evidence:\n" + "\n".join(lines)


def citations_from_search(chunk_results: list[tuple[int, float]],
                           metadata: list[dict]) -> list[Citation]:
    """Turn raw FAISS results into real Citation objects.

    This is the piece the earlier chapters never wired up: `metadata[idx]`
    -- a real report filename, page number, and report date -- came from
    Chapter 8's build_chunk_metadata_index(), which in turn came from
    Chapter 7's page-aware chunk_pages_by_tokens() (page) and the report's
    own filename (date). A Citation here is never invented -- it's read
    straight off the chunk that actually matched.

    A single report/page can supply more than one of the top-k chunks
    (a long page gets split into several chunks, and more than one can
    be relevant). Without deduplication the Evidence list would cite the
    same report/page several times and hide how many *distinct* sources
    actually back the answer, so only the first, best-ranked chunk from
    each (report, page) pair is kept.
    """
    citations = []
    seen_report_pages = set()
    for idx, _score in chunk_results:
        report_page = (metadata[idx]["report"], metadata[idx]["page"])
        if report_page in seen_report_pages:
            continue
        seen_report_pages.add(report_page)
        citations.append(Citation(report=metadata[idx]["report"], page=metadata[idx]["page"],
                                   report_date=metadata[idx].get("date")))
    return citations


def find_date_gaps(report_dates: list[str]) -> list[tuple[str, str]]:
    """Given a list of ISO date strings, find every run of consecutive
    missing days between the earliest and latest date.

    This only looks at the SEQUENCE of dates, not report content -- the
    idea is to catch "we have no report at all for this day," which
    content-based checks can't see (there's no content to check).
    """
    dates = sorted(date.fromisoformat(d) for d in report_dates)
    gaps = []
    for prev, curr in zip(dates, dates[1:]):
        missing_days = (curr - prev).days - 1
        if missing_days > 0:
            # The gap spans the day after `prev` through the day before `curr`.
            gaps.append(((prev + timedelta(days=1)).isoformat(), (curr - timedelta(days=1)).isoformat()))
    return gaps


if __name__ == "__main__":
    citations = [Citation(report="FORGE-16A-78-32_Drilling_038_2020-11-26.pdf", page=1)]
    print(format_evidence(citations))

    print()
    sample_dates = ["2020-10-22", "2020-11-07", "2020-11-24", "2020-11-25",
                     "2020-11-26", "2020-11-27", "2020-12-06", "2020-12-07",
                     "2020-12-08", "2021-01-06"]
    gaps = find_date_gaps(sample_dates)
    print(f"Gaps found in the Part I sample's ten dates: {len(gaps)}")
    for start, end in gaps:
        print(f"  {start} to {end}")

    print("\n--- Citations built from a real chunk-level search, not hardcoded ---")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_04"))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_08"))
    from build_faiss_index import build_chunk_metadata_index, search  # noqa: E402
    from semantic_search import MODEL_NAME  # noqa: E402
    from sentence_transformers import SentenceTransformer  # noqa: E402

    text_dir = Path("datasets/ddr_text")
    if text_dir.exists():
        model = SentenceTransformer(MODEL_NAME, device="cpu")
        index, metadata = build_chunk_metadata_index(text_dir, model)
        query_vec = model.encode(["stuck pipe"], normalize_embeddings=True)[0]
        results = search(index, query_vec, top_k=3)
        real_citations = citations_from_search(results, metadata)
        print(format_evidence(real_citations))
    else:
        print(f"{text_dir} does not exist -- run Chapter 1's batch extraction first.")
