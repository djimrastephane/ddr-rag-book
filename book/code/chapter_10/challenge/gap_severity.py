"""Chapter 10 challenge solution: classify each date gap's severity.

- Low: a short gap (under 3 days) within the same report type.
- High: a gap that crosses a report-type boundary (Drilling to
  Completion, as this archive's real gap does), regardless of length --
  a boundary crossing likely means an operational transition happened
  with no report covering it at all.

Usage:
    python code/chapter_10/challenge/gap_severity.py
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from traceable_answers import find_date_gaps  # noqa: E402

ARCHIVE_DIR = Path("datasets/forge_archive")


def parse_archive_filenames(archive_dir: Path) -> list[tuple[str, str]]:
    """Real filenames look like FORGE-16A-78-32_Drilling_076_2021-01-03.pdf
    -- pull out (date, report_type) for every report in the archive."""
    records = []
    for path in sorted(archive_dir.glob("*.pdf")):
        m = re.match(r"FORGE-16A-78-32_(\w+)_\d+_(\d{4}-\d{2}-\d{2})\.pdf", path.name)
        if m:
            report_type, iso_date = m.group(1), m.group(2)
            records.append((iso_date, report_type))
    return records


def classify_gap_severity(gap_start: str, gap_end: str,
                           date_to_type: dict[str, str]) -> str:
    """Look at the report type immediately before and after the gap. If
    they differ, the gap spans a real operational transition -- High,
    regardless of how many days it covers. Otherwise, severity depends
    only on length."""
    start_date = date.fromisoformat(gap_start)
    end_date = date.fromisoformat(gap_end)
    gap_days = (end_date - start_date).days + 1

    before_type = date_to_type.get((start_date - timedelta(days=1)).isoformat())
    after_type = date_to_type.get((end_date + timedelta(days=1)).isoformat())

    if before_type and after_type and before_type != after_type:
        return f"High (crosses {before_type} -> {after_type} boundary)"
    return "Low" if gap_days < 3 else "Medium"


if __name__ == "__main__":
    if not ARCHIVE_DIR.exists():
        raise SystemExit(f"{ARCHIVE_DIR} does not exist -- see Appendix A for how to obtain it.")

    records = parse_archive_filenames(ARCHIVE_DIR)
    date_to_type = dict(records)
    all_dates = [d for d, _type in records]

    gaps = find_date_gaps(all_dates)
    print(f"Gaps found in the full 76-report archive: {len(gaps)}\n")
    for start, end in gaps:
        severity = classify_gap_severity(start, end, date_to_type)
        print(f"  {start} to {end}: severity = {severity}")

    assert len(gaps) == 1, "expected exactly one real gap in the full archive"
    assert "High" in classify_gap_severity(*gaps[0], date_to_type), \
        "expected the real Drilling-to-Completion gap to classify as High"
    print("\nConfirmed: the real Jan 4-5 gap correctly classifies as High "
          "(it crosses the Drilling-to-Completion boundary).")
