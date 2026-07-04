"""Chapter 6 challenge solution: find the corruption level at which the
quality gate starts rejecting text, since this archive has no real
scanned page to test against.

Usage:
    python code/chapter_06/challenge/corruption_stress_test.py
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ocr_quality_gate import evaluate_ocr_quality  # noqa: E402

GARBAGE_SYMBOLS = "|#~^*_=+<>{}[]"


def corrupt_word(word: str, rng: random.Random) -> str:
    """Replace a word with symbol-heavy noise, the way OCR misreads a
    smudged or low-resolution glyph run -- not just character lookalikes,
    but genuinely non-alphabetic garbage of similar length."""
    length = max(1, len(word))
    return "".join(rng.choice(GARBAGE_SYMBOLS) for _ in range(length))


def corrupt_text(text: str, severity: float, rng: random.Random) -> str:
    """severity in [0, 1]: fraction of words replaced with symbol garbage.
    This is what actually degrades both signals the gate checks --
    alphabetic word count drops, and symbol ratio rises -- unlike simple
    character-swapping, which barely moves either."""
    words = text.split(" ")
    corrupted_words = [
        corrupt_word(w, rng) if rng.random() < severity else w
        for w in words
    ]
    return " ".join(corrupted_words)


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    sample_path = sorted(text_dir.glob("*.txt"))[0]
    clean_text = sample_path.read_text(encoding="utf-8")

    rng = random.Random(42)
    print(f"Stress-testing against {sample_path.name}\n")
    first_rejection = None
    for severity_pct in range(0, 101, 10):
        severity = severity_pct / 100
        corrupted = corrupt_text(clean_text, severity, rng)
        result = evaluate_ocr_quality(corrupted)
        print(f"severity={severity_pct:3d}%  reject={result['reject_ocr']}  "
              f"flags={result['flags']}  symbol_ratio={result['symbol_ratio']:.3f}")
        if result["reject_ocr"] and first_rejection is None:
            first_rejection = severity_pct

    print(f"\nGate starts rejecting at approximately {first_rejection}% corruption "
          f"severity on this sample report.")
