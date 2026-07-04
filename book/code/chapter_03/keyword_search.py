"""Chapter 3: keyword search over cleaned DDR text via an inverted index.

Usage:
    python code/chapter_03/keyword_search.py "stuck"
    python code/chapter_03/keyword_search.py "packers fishing"
"""

import re
import sys
from collections import defaultdict
from pathlib import Path


def tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens, dropping punctuation.

    Lowercasing means "stuck" and "STUCK" are treated as the same word.
    The regex only keeps letters and digits, so "6,507'" becomes "6" and
    "507" -- punctuation can't create accidental non-matches.
    """
    return re.findall(r"[a-z0-9]+", text.lower())


def build_index(text_dir: Path) -> dict[str, set[str]]:
    """Build an inverted index: for every word, which files contain it.

    This is the "invert" in inverted index -- instead of "what words are
    in file X" (which needs scanning the whole file), we can now ask
    "which files contain word Y" as a single dictionary lookup.
    """
    index: dict[str, set[str]] = defaultdict(set)
    for path in sorted(text_dir.glob("*.txt")):
        tokens = set(tokenize(path.read_text(encoding="utf-8")))
        for token in tokens:
            index[token].add(path.name)
    return index


def search(index: dict[str, set[str]], query: str) -> set[str]:
    """AND search: a document must contain every query token to match.

    Start with the set of files containing the first query word, then
    intersect (`&=`) with each subsequent word's file set. Whatever's
    left at the end contains every word in the query.
    """
    query_tokens = tokenize(query)
    if not query_tokens:
        return set()
    results = index.get(query_tokens[0], set()).copy()
    for token in query_tokens[1:]:
        results &= index.get(token, set())
    return results


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text_expanded")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 2's expand_abbreviations.py first.")

    query = " ".join(sys.argv[1:]) or "stuck"
    index = build_index(text_dir)
    results = search(index, query)
    print(f"Query: {query!r}")
    for name in sorted(results):
        print(f"  {name}")
    if not results:
        print("  (no results)")
