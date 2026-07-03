"""Curate the Part I sample DDR archive from the public Utah FORGE dataset.

This book uses real, publicly available Daily Drilling Reports from the
Utah FORGE project (a DOE-funded enhanced geothermal system research
well, FORGE 16A(78)-32, operated by the University of Utah). The full
archive is public; this script selects a small, narratively coherent
subset for Part I so early chapters stay approachable, and copies them
with clean, consistent filenames.

The curated output is already committed to datasets/sample_ddrs/ in this
repository, so most readers never need to run this script. It's included
for transparency: this is exactly how that subset was produced from the
full public archive.

Usage:
    python code/chapter_01/build_sample_archive.py --source /path/to/utah_forge_archive
"""

import argparse
import shutil
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "datasets" / "sample_ddrs"

# (report_no, date, report_type, source filename substring to match, clean-name suffix)
CURATED_REPORTS = [
    (3, "2020-10-22", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_10222020_10222020_19_reporttmp.pdf"),
    (19, "2020-11-07", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_11072020_11072020_24_reporttmp.pdf"),
    (36, "2020-11-24", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_11242020_11242020_9_1_reporttmp.pdf"),
    (37, "2020-11-25", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_11252020_11252020_15_reporttmp.pdf"),
    (38, "2020-11-26", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_11262020_11262020_11_reporttmp.pdf"),
    (39, "2020-11-27", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_11272020_11272020_9_reporttmp.pdf"),
    (48, "2020-12-06", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_12062020_12062020_17_reporttmp.pdf"),
    (49, "2020-12-07", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_12072020_12072020_3_reporttmp.pdf"),
    (50, "2020-12-08", "Drilling", "Utah_Forge_FORGE_16A_(78)-32_Drilling-C_12082020_12082020_10_reporttmp.pdf"),
    (3, "2021-01-06", "Completion", "Utah_Forge_FORGE_16A_(78)-32_Completion-C_01062021_01062021_1_tmp.pdf"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, required=True,
        help="Path to a local copy of the public Utah FORGE DDR archive (data/raw folder)",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for report_no, date, report_type, source_name in CURATED_REPORTS:
        src = args.source / source_name
        if not src.exists():
            print(f"[skip] not found: {source_name}")
            continue
        dest_name = f"FORGE-16A-78-32_{report_type}_{report_no:03d}_{date}.pdf"
        dest = OUTPUT_DIR / dest_name
        shutil.copyfile(src, dest)
        print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
