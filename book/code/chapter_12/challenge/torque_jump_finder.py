"""Chapter 12 challenge solution: find every real day-over-day TORQUE
jump greater than 25% across the full 76-report archive, and check how
many actually correspond to a notable narrative event.

Usage:
    python code/chapter_12/challenge/torque_jump_finder.py
"""

import re
import sys
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from torque_trend_check import torque_trend  # noqa: E402

ARCHIVE_DIR = Path("datasets/forge_archive")

# Keywords that suggest a genuinely notable operational event, to check
# each real jump against -- not a rigorous classifier, just a quick way
# to separate "something happened" days from ordinary drilling days.
EVENT_KEYWORDS = ["stuck", "lost", "twist", "fishing", "wash out", "kick", "influx"]


def extract_torque_and_date(pdf_path: Path) -> tuple[str, float, str] | None:
    """Pull the report date and header TORQUE value out of one PDF.
    Returns (iso_date, torque_value, full_text) or None if either field
    is missing."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join((page.extract_text() or "") for page in pdf.pages)

    date_m = re.search(r"RPT DATE:\s*([0-9/]+)", text)
    torque_m = re.search(r"TORQUE:\s*([\d,]+)", text)
    if not date_m or not torque_m:
        return None

    month, day, year = (int(x) for x in date_m.group(1).split("/"))
    iso_date = f"{year:04d}-{month:02d}-{day:02d}"
    torque_value = float(torque_m.group(1).replace(",", ""))
    return iso_date, torque_value, text


if __name__ == "__main__":
    if not ARCHIVE_DIR.exists():
        raise SystemExit(f"{ARCHIVE_DIR} does not exist -- see Appendix A for how to obtain it.")

    records = []
    for pdf_path in sorted(ARCHIVE_DIR.glob("*.pdf")):
        parsed = extract_torque_and_date(pdf_path)
        if parsed:
            iso_date, torque_value, text = parsed
            records.append((iso_date, torque_value, text))

    records.sort(key=lambda r: r[0])
    readings = [(d, v) for d, v, _t in records]
    text_by_date = {d: t for d, _v, t in records}

    trend = torque_trend(readings)
    big_jumps = [(date, val, pct) for date, val, pct in trend if abs(pct) > 0.25]

    print(f"Found {len(records)} reports with a TORQUE header value.")
    print(f"Found {len(big_jumps)} day-over-day jumps greater than 25%:\n")

    notable_count = 0
    for date, val, pct in big_jumps:
        text = text_by_date[date].lower()
        matched_keywords = [kw for kw in EVENT_KEYWORDS if kw in text]
        is_notable = bool(matched_keywords)
        notable_count += is_notable
        flag = f"notable ({', '.join(matched_keywords)})" if is_notable else "unremarkable"
        print(f"  {date}: {val:.0f} ({pct:+.1%})  -- {flag}")

    print(f"\n{notable_count} of {len(big_jumps)} large torque jumps coincide with "
          f"an event keyword in that day's report text.")
