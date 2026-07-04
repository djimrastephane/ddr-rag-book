"""Chapter 6: a quality gate for OCR (or any extracted) text.

Usage:
    python code/chapter_06/ocr_quality_gate.py datasets/ddr_text/FORGE-16A-78-32_Drilling_038_2020-11-26.txt
"""

import re
import sys
from pathlib import Path


def evaluate_ocr_quality(text: str, min_chars: int = 200,
                          min_alpha_words: int = 30,
                          max_symbol_ratio: float = 0.35,
                          reject_min_flags: int = 2) -> dict:
    """Score extracted text against two cheap heuristics and decide
    whether to trust it.

    - low_text_density: is there simply not enough text (or not enough
      real words) for this to plausibly be a genuine, fully-read page?
    - high_symbol_ratio: is a large fraction of the non-whitespace
      content made up of symbols rather than letters/digits -- the kind
      of noise a bad OCR pass produces?

    Neither flag alone is rejected on -- reject_min_flags=2 means BOTH
    have to fire before the page is flagged. This avoids false positives
    on legitimate pages that happen to trip just one heuristic (e.g. a
    short report that's genuinely short, not corrupted).
    """
    alpha_tokens = re.findall(r"[A-Za-z]+", text)
    non_ws = [c for c in text if not c.isspace()]
    # "Noisy" characters are anything that's neither a letter/digit nor one
    # of the punctuation marks real DDR text commonly and legitimately uses.
    noisy = sum(1 for c in non_ws if not c.isalnum() and c not in set("%.,()/-:'"))
    symbol_ratio = noisy / max(len(non_ws), 1)

    flags = {
        "low_text_density": len(text) < min_chars or len(alpha_tokens) < min_alpha_words,
        "high_symbol_ratio": symbol_ratio > max_symbol_ratio,
    }
    active = [k for k, v in flags.items() if v]
    return {
        "reject_ocr": len(active) >= reject_min_flags,
        "flags": flags,
        "chars": len(text),
        "alpha_words": len(alpha_tokens),
        "symbol_ratio": symbol_ratio,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python ocr_quality_gate.py <path-to-text-file>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    result = evaluate_ocr_quality(text)
    print(f"{path.name}: {result}")
