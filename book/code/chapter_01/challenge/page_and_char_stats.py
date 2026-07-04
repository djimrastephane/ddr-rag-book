"""Chapter 1 challenge solution: print page/character counts per PDF, and
compare the sparsest report (#3, before spud) against a content-rich one
(#38, the stuck-pipe day).

Usage:
    python code/chapter_01/challenge/page_and_char_stats.py
"""

import re
import sys
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from read_ddr import extract_text  # noqa: E402

SAMPLE_DIR = Path("datasets/sample_ddrs")


def report_stats(pdf_path: Path) -> dict:
    """Page count, character count, and the header fields the challenge
    hints at (SPUD DATE, DFS, DOL) -- pulled with the same kind of small
    regex used throughout this book to read specific fields out of a
    DDR's free-text header."""
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
    text = extract_text(pdf_path)

    spud_date_m = re.search(r"SPUD DATE:\s*([0-9/]*)", text)
    dfs_m = re.search(r"DFS:\s*(\d*)", text)
    dol_m = re.search(r"DOL:\s*(\d*)", text)

    return {
        "pages": num_pages,
        "chars": len(text),
        "spud_date": spud_date_m.group(1) if spud_date_m else "",
        "dfs": dfs_m.group(1) if dfs_m else "",
        "dol": dol_m.group(1) if dol_m else "",
    }


if __name__ == "__main__":
    for name in ["FORGE-16A-78-32_Drilling_003_2020-10-22.pdf",
                 "FORGE-16A-78-32_Drilling_038_2020-11-26.pdf"]:
        stats = report_stats(SAMPLE_DIR / name)
        print(f"{name}:")
        print(f"  pages={stats['pages']}  chars={stats['chars']}")
        print(f"  SPUD DATE={stats['spud_date']!r}  DFS={stats['dfs']!r}  DOL={stats['dol']!r}")
        print()

    print("Report #3's SPUD DATE is blank and DFS is empty -- the well hadn't")
    print("spudded yet, so there's no 'days from spud' to report. Report #38's")
    print("header, by contrast, shows a real spud date and a populated DFS/DOL,")
    print("plus a fully worked BHA, casing, and survey data section -- all of")
    print("which adds to its much larger character count.")
