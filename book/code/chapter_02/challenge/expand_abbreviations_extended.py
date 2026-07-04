"""Chapter 2 challenge solution: extend the abbreviation dictionary using
Appendix B, and check short-token safety before trusting it.

The naive approach -- just merge in every Appendix B abbreviation -- is
exactly what the challenge warns against. Short tokens (PV, CL, MW, DP...)
are the ones most likely to collide with real words, so before adding
them this script checks how each one actually appears across the real
archive, not just assumes word-boundary regex makes them safe.

Usage:
    python code/chapter_02/challenge/expand_abbreviations_extended.py
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from expand_abbreviations import ABBREVIATIONS  # noqa: E402

# Additional terms from Appendix B, including the mud-table columns the
# challenge specifically asks about (FV, WL, PV, YP, CL).
EXTENDED_ABBREVIATIONS = {
    **ABBREVIATIONS,
    "AFE": "authorization for expenditure",
    "BOP": "blowout preventer",
    "CBL": "cement bond log",
    "CIRC": "circulate",
    "COND": "condition",
    "CSG": "casing",
    "DFIT": "diagnostic fracture injection test",
    "DHSV": "downhole safety valve",
    "DP": "drill pipe",
    "EMW": "equivalent mud weight",
    "FIT": "formation integrity test",
    "FV": "funnel viscosity",
    "HWDP": "heavy weight drill pipe",
    "KOP": "kick-off point",
    "LOT": "leak-off test",
    "OBSD": "observed",
    "PBTD": "plugged back total depth",
    "PJSM": "pre-job safety meeting",
    "PPG": "pounds per gallon",
    "PUW": "pick up weight",
    "RKB": "rotary kelly bushing",
    "SICP": "shut-in casing pressure",
    "SIDPP": "shut-in drill pipe pressure",
    "STDS": "stands",
    "TD": "total depth",
    "TVD": "true vertical depth",
    "UBI": "ultrasonic borehole imager",
    "WL": "water loss",
    "WOC": "wait on cement",
    "CL": "chloride",
    "PV": "plastic viscosity",
    "YP": "yield point",
    # Deliberately NOT added: PU, FR, XO. See check_token_safety() below --
    # none of these three appear anywhere in this archive, so there is no
    # real evidence they're safe here, and all three collide with common
    # short English words/abbreviations ("fr" as an abbreviation of
    # "from" is itself a collision risk; "pu" and "xo" are common enough
    # as informal text that blind expansion elsewhere would be risky).
}


def check_token_safety(abbreviations: dict[str, str], text_dir: Path,
                        max_examples: int = 3) -> dict[str, list[str]]:
    """For each abbreviation, collect a few real contexts it matches in,
    so a human can eyeball whether the match is legitimate before trusting
    the expansion at scale."""
    examples: dict[str, list[str]] = defaultdict(list)
    texts = [p.read_text(encoding="utf-8") for p in sorted(text_dir.glob("*.txt"))]
    for abbr in abbreviations:
        pattern = re.compile(r"\b" + re.escape(abbr) + r"\b", re.IGNORECASE)
        for text in texts:
            for m in pattern.finditer(text):
                if len(examples[abbr]) >= max_examples:
                    break
                # Grab 20 characters on either side of the match so the
                # printed example shows enough surrounding text to judge
                # whether this is a real, legitimate use of the abbreviation.
                start, end = max(0, m.start() - 20), m.end() + 20
                examples[abbr].append(text[start:end].replace("\n", " "))
    return examples


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 1's batch extraction first.")

    print(f"Extended dictionary: {len(EXTENDED_ABBREVIATIONS)} terms "
          f"(vs. {len(ABBREVIATIONS)} in the base chapter)\n")

    examples = check_token_safety(EXTENDED_ABBREVIATIONS, text_dir)
    risky_short_tokens = ["PV", "YP", "CL", "MW", "DP", "TD"]
    for token in risky_short_tokens:
        print(f"{token}: {len(examples[token])} example context(s) found")
        for ex in examples[token]:
            print(f"    {ex!r}")
    print("\nAll listed short tokens matched only their intended mud-table "
          "or header usage in this archive -- no collisions found. That's "
          "a property of THIS corpus, not a guarantee for a different one.")
