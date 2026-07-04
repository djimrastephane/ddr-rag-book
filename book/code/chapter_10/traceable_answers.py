"""Chapter 10: format citations, and detect gaps in report coverage.

Usage:
    python code/chapter_10/traceable_answers.py
"""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class Citation:
    report: str
    page: int | None = None


def format_evidence(citations: list[Citation]) -> str:
    """Turn a list of citations into a human-readable evidence block --
    the same format used throughout this book's answers, so a claim is
    never presented without a way to check it against the source."""
    lines = [f"  {c.report}" + (f" page {c.page}" if c.page else "") for c in citations]
    return "Evidence:\n" + "\n".join(lines)


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
