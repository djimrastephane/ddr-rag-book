"""Copy the full public Utah FORGE DDR archive into this repository.

Part II's 'at scale' chapters (8, 9, 11, 12) work against the complete
FORGE 16A(78)-32 archive rather than Part I's 10-report curated subset.
The source archive has duplicate filenames for each report (one using
parentheses, one using square brackets, both identical in content) plus
some "reporttmp 2.pdf" copy artefacts; this script deduplicates and
renames to a clean, sequential convention: FORGE-16A-78-32_<Type>_<report
number>_<date>.pdf.

Report numbers and dates are parsed from each PDF's own header (RPT
DATE / RPT NUM fields), not from the source filename — the source
filenames are inconsistent (see Chapter 6/Appendix A for why), but the
report content itself is reliable.

The curated output is already committed to datasets/forge_archive/ in
this repository. This script is included for transparency and so readers
can reproduce it against their own copy of the public archive.

Usage:
    python code/chapter_08/build_full_archive.py --source /path/to/utah_forge_archive
"""

import argparse
import re
import shutil
from pathlib import Path

import pdfplumber

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "datasets" / "forge_archive"


def parse_report_date_and_number(pdf_path: Path) -> tuple[str, int, str] | None:
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    date_m = re.search(r"RPT DATE:\s*([0-9/]+)", text)
    num_m = re.search(r"RPT NUM\.?:\s*(\d+)", text)
    if not date_m or not num_m:
        return None
    month, day, year = (int(x) for x in date_m.group(1).split("/"))
    if year < 100:
        year += 2000
    iso_date = f"{year:04d}-{month:02d}-{day:02d}"
    report_type = "Completion" if "Completion-C" in pdf_path.name else "Drilling"
    return iso_date, int(num_m.group(1)), report_type


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, required=True,
        help="Path to a local copy of the public Utah FORGE DDR archive (data/raw folder)",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = sorted(
        p for p in args.source.glob("*.pdf") if not p.name.endswith(" 2.pdf")
    )

    seen: set[tuple[str, str]] = set()
    written = 0
    for src in candidates:
        parsed = parse_report_date_and_number(src)
        if parsed is None:
            print(f"[skip: unparseable] {src.name}")
            continue
        iso_date, report_no, report_type = parsed
        key = (report_type, iso_date)
        if key in seen:
            continue  # duplicate filename variant of a report already copied
        seen.add(key)

        dest_name = f"FORGE-16A-78-32_{report_type}_{report_no:03d}_{iso_date}.pdf"
        shutil.copyfile(src, OUTPUT_DIR / dest_name)
        written += 1

    print(f"Wrote {written} unique reports to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
