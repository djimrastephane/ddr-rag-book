"""Chapter 9 challenge solution: implement and test the two numerical
guards from the chapter's "Reading the real fusion code" case study.

Guard 1: the classic BM25 IDF formula, log((N - df + 0.5) / (df + 0.5)),
goes NEGATIVE when a term appears in almost every document (df close to
N). The companion pipeline's fix wraps the ratio as log(1.0 + ratio),
which can never go below log(1.0) = 0.

Guard 2: min-max normalization -- (score - min) / (max - min) -- divides
by zero when every candidate in a batch scores identically (max == min).
The companion pipeline's fix returns a neutral value in that case instead
of crashing.

Usage:
    python code/chapter_09/challenge/scoring_guards.py
"""

import math


def idf_unguarded(n_docs: int, df: int) -> float:
    """The classic Robertson-Sparse-Selection IDF -- no guard."""
    return math.log((n_docs - df + 0.5) / (df + 0.5))


def idf_guarded(n_docs: int, df: int) -> float:
    """Wrapping the ratio as 1.0 + ratio before the log guarantees a
    non-negative result for every possible df, because 1.0 + ratio can
    never fall below 1.0 (and log(1.0) = 0)."""
    return math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))


def minmax_normalize_unguarded(scores: list[float]) -> list[float]:
    """No guard: divides by zero (raising ZeroDivisionError) whenever
    every score in the batch is identical."""
    lo, hi = min(scores), max(scores)
    return [(s - lo) / (hi - lo) for s in scores]


def minmax_normalize_guarded(scores: list[float]) -> list[float]:
    """If every score ties (hi <= lo), there's no meaningful way to
    rescale into [0, 1] -- return a neutral 0.0 for everyone instead of
    dividing by zero. In a fused ranking, this just means the OTHER
    signal is left free to break the tie."""
    lo, hi = min(scores), max(scores)
    if hi <= lo:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


if __name__ == "__main__":
    # Edge case 1: a term that appears in 9 of 10 documents -- almost universal.
    n_docs, df = 10, 9
    print(f"IDF for a near-universal term (n_docs={n_docs}, df={df}):")
    try:
        unguarded = idf_unguarded(n_docs, df)
        print(f"  unguarded: {unguarded:.4f}", "<- NEGATIVE" if unguarded < 0 else "")
    except ValueError as e:
        print(f"  unguarded: raised {e}")
    guarded = idf_guarded(n_docs, df)
    print(f"  guarded:   {guarded:.4f} (always >= 0)")
    assert guarded >= 0

    # Edge case 2: every candidate in a batch scores identically.
    tied_scores = [0.42, 0.42, 0.42, 0.42]
    print(f"\nMin-max normalization on a tied batch {tied_scores}:")
    try:
        minmax_normalize_unguarded(tied_scores)
        print("  unguarded: did not raise (unexpected)")
    except ZeroDivisionError as e:
        print(f"  unguarded: raised ZeroDivisionError ({e}) -- confirmed it fails first")
    guarded_result = minmax_normalize_guarded(tied_scores)
    print(f"  guarded:   {guarded_result} (no crash, neutral value for every candidate)")
    assert guarded_result == [0.0, 0.0, 0.0, 0.0]

    print("\nBoth guards confirmed: the unguarded version fails on its edge case, "
          "the guarded version handles it safely.")
