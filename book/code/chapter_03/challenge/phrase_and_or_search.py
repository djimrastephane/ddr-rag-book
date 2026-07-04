"""Chapter 3 challenge solution: phrase search and an OR operator.

Usage:
    python code/chapter_03/challenge/phrase_and_or_search.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from keyword_search import build_index, tokenize  # noqa: E402


def phrase_search(text_dir: Path, phrase: str) -> set[str]:
    """Tokens must appear adjacent and in order, not just co-occur.

    Unlike the base chapter's AND search (which only checks that both
    words exist *somewhere* in the document), this slides a window the
    length of the phrase across every position in the document's token
    list and checks for an exact sequence match -- so "pipe free" matches
    only where those two words appear next to each other, in that order.
    """
    phrase_tokens = tokenize(phrase)
    matches = set()
    for path in sorted(text_dir.glob("*.txt")):
        doc_tokens = tokenize(path.read_text(encoding="utf-8"))
        n = len(phrase_tokens)
        for i in range(len(doc_tokens) - n + 1):
            if doc_tokens[i:i + n] == phrase_tokens:
                matches.add(path.name)
                break
    return matches


def search_or(index: dict[str, set[str]], query: str) -> set[str]:
    """OR search: a document matches if it contains ANY query token."""
    results: set[str] = set()
    for token in tokenize(query):
        results |= index.get(token, set())
    return results


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text_expanded")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 2's expand_abbreviations.py first.")

    index = build_index(text_dir)

    stuck_hits = search_or(index, "stuck")  # single token, OR == AND here
    print("search('stuck'):", sorted(stuck_hits))
    assert stuck_hits == {"FORGE-16A-78-32_Drilling_038_2020-11-26.txt"}, "expected only report #38"

    or_hits = search_or(index, "packers fishing")
    print("search_or('packers fishing'):", sorted(or_hits))
    assert "FORGE-16A-78-32_Drilling_049_2020-12-07.txt" in or_hits
    assert "FORGE-16A-78-32_Drilling_050_2020-12-08.txt" in or_hits

    phrase_hits = phrase_search(text_dir, "pipe free")
    print("phrase_search('pipe free'):", sorted(phrase_hits))

    print("\nAll assertions passed.")
