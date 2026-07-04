"""Chapter 2: expand oilfield abbreviations in extracted DDR text.

Reads the .txt files Chapter 1 produced in datasets/ddr_text/, expands
every known abbreviation using word-boundary regex substitution, and
writes the results to datasets/ddr_text_expanded/.

Usage:
    python code/chapter_02/expand_abbreviations.py
    python code/chapter_02/expand_abbreviations.py --in-dir datasets/ddr_text --out-dir datasets/ddr_text_expanded
"""

import argparse
import re
from pathlib import Path

ABBREVIATIONS = {
    "BHA": "bottom hole assembly",
    "WOB": "weight on bit",
    "RPM": "revolutions per minute",
    "ROP": "rate of penetration",
    "MD": "measured depth",
    "TVD": "true vertical depth",
    "SPP": "stand pipe pressure",
    "GPM": "gallons per minute",
    "DLS": "dogleg severity",
    "MWD": "measurement while drilling",
    "NMDC": "non-magnetic drill collar",
    "UBHO": "universal bottom hole orientation sub",
    "NPT": "non-productive time",
    "ECD": "equivalent circulating density",
    "MW": "mud weight",
    "DFS": "days from spud",
    "DOL": "days on location",
    "PDC": "polycrystalline diamond compact",
}


def expand_text(text: str, abbreviations: dict[str, str] = ABBREVIATIONS) -> str:
    """Replace every whole-word match of an abbreviation with its expansion.

    `\\b...\\b` (word boundary) is the important part here: without it,
    re.sub would also match the abbreviation as a *substring* of an
    unrelated word (e.g. "MD" inside a longer token), silently corrupting
    text it was never meant to touch. re.IGNORECASE means "BHA", "bha",
    and "Bha" all match the same way.
    """
    for abbr, expansion in abbreviations.items():
        pattern = r"\b" + re.escape(abbr) + r"\b"
        text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in-dir", type=Path, default=Path("datasets/ddr_text"))
    parser.add_argument("--out-dir", type=Path, default=Path("datasets/ddr_text_expanded"))
    args = parser.parse_args()

    if not args.in_dir.exists():
        raise SystemExit(
            f"{args.in_dir} does not exist yet. Run Chapter 1's read_ddr.py in "
            f"--batch mode first: python code/chapter_01/read_ddr.py "
            f"datasets/sample_ddrs/ --batch --out {args.in_dir}"
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    # Same filename in the output folder, so a reader can always find the
    # expanded version of a report by matching names across the two folders.
    for path in sorted(args.in_dir.glob("*.txt")):
        expanded = expand_text(path.read_text(encoding="utf-8"))
        out_path = args.out_dir / path.name
        out_path.write_text(expanded, encoding="utf-8")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
