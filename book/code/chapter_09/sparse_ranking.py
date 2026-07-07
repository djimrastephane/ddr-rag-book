"""Chapter 9: a ranked sparse retriever (BM25).

Chapter 3's search() returns an unordered SET -- a report either contains
every query word or it doesn't, with no notion of "best match first."
Reciprocal Rank Fusion needs a ranked LIST. This module supplies the
missing ranked sparse signal, so Chapter 9's fusion has two real ranked
inputs to combine: this one, and Chapter 4's dense semantic ranking.

Usage:
    python code/chapter_09/sparse_ranking.py "packers fishing"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_03"))
from keyword_search import tokenize  # noqa: E402


def rank_bm25(text_dir: Path, query: str) -> list[str]:
    """Rank every report in text_dir best-first for a query, using BM25.

    BM25 is Chapter 3's keyword search turned into a ranking. Instead of
    just "does this report contain the words," it scores each report by
    how often the query's words appear -- weighted so a rare, specific
    word ("packers") counts more than a common one ("the"), and adjusted
    for report length so a long report doesn't win just by containing
    more words overall.

    Falls back to a plain term-frequency count if `rank-bm25` isn't
    installed, so this exercise still runs and still returns a real
    ranking (just a cruder one).
    """
    paths = sorted(text_dir.glob("*.txt"))
    corpus = [tokenize(p.read_text(encoding="utf-8")) for p in paths]
    query_tokens = tokenize(query)

    try:
        from rank_bm25 import BM25Okapi
        scores = BM25Okapi(corpus).get_scores(query_tokens)
    except ImportError:
        query_set = set(query_tokens)
        scores = [sum(1 for token in doc if token in query_set) for doc in corpus]

    ranked = sorted(zip(paths, scores), key=lambda pair: pair[1], reverse=True)
    return [path.name for path, _score in ranked]


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 1's batch extraction first.")

    query = " ".join(sys.argv[1:]) or "packers fishing"
    print(f"BM25 ranking for {query!r} (best match first):")
    for rank, name in enumerate(rank_bm25(text_dir, query), start=1):
        print(f"  {rank:2d}. {name}")
