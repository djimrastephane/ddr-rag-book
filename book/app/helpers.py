"""Pure logic for the DDR RAG Companion App.

Kept separate from the Streamlit UI so it can be tested without a browser
and imported without pulling in Streamlit. The heavy book modules
(retrieval, generation) are imported lazily inside run_query(), so the
small text helpers below stay fast to import and test.

The retrieval and generation here reuse the book's own code directly:
  - retrieval:  hybrid_search()  from code/chapter_09/hybrid_search.py
  - prompt:     build_prompt()   from code/chapter_05/first_rag.py
  - generation: ollama_llm_call() from code/chapter_05/first_rag.py
Nothing about the pipeline is reimplemented here.
"""

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Make the book's chapter modules importable, wherever this app is run from.
_BOOK = Path(__file__).resolve().parents[1]          # .../book
for _chapter in ("chapter_01", "chapter_04", "chapter_05", "chapter_09"):
    _path = str(_BOOK / "code" / _chapter)
    if _path not in sys.path:
        sys.path.insert(0, _path)

# The extracted-text folder is generated (Chapter 1's batch extraction), not
# committed -- so on a fresh clone it's empty. SAMPLE_DDRS holds the committed
# source PDFs; ensure_text_dir() below rebuilds the text folder from them if
# it's missing, so the app works straight from a clean checkout.
TEXT_DIR = _BOOK / "datasets" / "ddr_text"
SAMPLE_DDRS = _BOOK / "datasets" / "sample_ddrs"
DEFAULT_MODEL = "qwen2.5:7b-instruct"
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_DOWN_MESSAGE = (
    "Ollama is not running. Retrieval still works. "
    "Start Ollama to generate an answer."
)

_REPORT_DATE = re.compile(r"_(\d{4}-\d{2}-\d{2})\.")
_REPORT_NUMBER = re.compile(r"_(?:Drilling|Completion)_(\d+)_")


def report_date(filename: str) -> str | None:
    """Read the report date straight off the filename (WellEz's own naming
    convention), the same way Chapter 8 does. Returns None if absent."""
    match = _REPORT_DATE.search(filename)
    return match.group(1) if match else None


def report_number(filename: str) -> str | None:
    """Read the report number straight off the filename
    (e.g. '..._Drilling_050_...' -> '050'). Returns None if absent."""
    match = _REPORT_NUMBER.search(filename)
    return match.group(1) if match else None


def _tokens(text: str) -> list[str]:
    """Chapter 3's tokenizer: lowercase words and numbers, no punctuation."""
    return re.findall(r"[a-z0-9]+", text.lower())


# Common words (and words every DDR contains) that carry no signal about
# *why* a specific report matched, so they're excluded from snippet
# centring and the "why it matters" line.
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "was", "were",
    "are", "its", "did", "not", "what", "which", "how", "who", "why",
    "around", "led", "report", "reports", "operation", "operations",
}


def _query_terms(query: str) -> list[str]:
    """Distinctive query words: unique, longer than two characters, and not
    a stopword. Used for both snippet centring and 'why it matters', so the
    two always agree on what counts as a match."""
    return [w for w in dict.fromkeys(_tokens(query)) if len(w) > 2 and w not in _STOPWORDS]


def best_snippet(text: str, query: str, width: int = 240) -> str:
    """Return a short excerpt from the window that covers the *most* of the
    query's words, so an evidence card shows why the report matched rather
    than the first stray keyword. (Centring on the first match alone lands
    'stuck pipe' on a 'Drill Pipe' table row and misses 'became stuck'.)
    Falls back to the report's opening if no query word appears."""
    flat = " ".join(text.split())
    low = flat.lower()
    terms = _query_terms(query)

    hits = []
    for term in terms:
        start = 0
        while True:
            pos = low.find(term, start)
            if pos == -1:
                break
            hits.append(pos)
            start = pos + len(term)
    if not hits:
        return flat[:width].strip() + ("…" if len(flat) > width else "")

    half = width // 2
    best_center, best_cover = hits[0], -1
    for pos in hits:
        window = low[max(0, pos - half):pos + half]
        cover = sum(1 for term in terms if term in window)
        if cover > best_cover:
            best_cover, best_center = cover, pos

    start = max(0, best_center - width // 3)
    end = min(len(flat), start + width)
    return ("…" if start > 0 else "") + flat[start:end].strip() + ("…" if end < len(flat) else "")


def matched_terms(text: str, query: str) -> list[str]:
    """Distinctive query words that actually appear in the report --
    derived, never invented. Substring match, so 'packer' counts as present
    in 'packers'. Used for a safe 'why it matters' line."""
    low = text.lower()
    return [w for w in _query_terms(query) if w in low]


def why_it_matters(text: str, query: str) -> str | None:
    """A safe, non-invented reason a report was retrieved: the query words
    it genuinely contains. Returns None when there's no literal overlap
    (the match was purely semantic), rather than making something up."""
    terms = matched_terms(text, query)
    if not terms:
        return None
    return "This report's text matches your question on: " + ", ".join(terms) + "."


def ollama_available(host: str = OLLAMA_HOST) -> bool:
    """True if a local Ollama server answers, so the UI can decide between
    generating an answer and showing retrieval only."""
    try:
        urllib.request.urlopen(host + "/api/tags", timeout=2)
        return True
    except (urllib.error.URLError, OSError):
        return False


def ensure_text_dir(text_dir=TEXT_DIR) -> Path:
    """Guarantee the extracted-text folder exists and is populated, so the
    app runs from a clean clone. If it's empty, rebuild it from the
    committed sample PDFs using Chapter 1's extraction -- exactly what the
    book's Chapter 1 batch step produces."""
    text_dir = Path(text_dir)
    if text_dir.exists() and any(text_dir.glob("*.txt")):
        return text_dir
    from read_ddr import extract_text  # code/chapter_01
    text_dir.mkdir(parents=True, exist_ok=True)
    for pdf_path in sorted(SAMPLE_DDRS.glob("*.pdf")):
        (text_dir / (pdf_path.stem + ".txt")).write_text(
            extract_text(pdf_path), encoding="utf-8")
    return text_dir


def run_query(question: str, model, text_dir=TEXT_DIR,
              top_k: int = 5, generate: bool = True,
              model_name: str = DEFAULT_MODEL) -> dict:
    """The whole companion pipeline in one call: retrieve, then (optionally)
    generate, and return everything needed to show the answer AND its
    evidence -- never the answer alone.

    Retrieval is Chapter 9's hybrid_search(); generation is Chapter 5's
    build_prompt() + ollama_llm_call(). Both are imported here, lazily, so
    importing this module for the text helpers above stays cheap. The text
    folder is rebuilt from the sample PDFs first if it's empty.
    """
    from hybrid_search import hybrid_search          # code/chapter_09
    from first_rag import build_prompt, ollama_llm_call  # code/chapter_05
    from semantic_search import load_chunks          # code/chapter_04

    text_dir = ensure_text_dir(text_dir)
    filenames, texts = load_chunks(text_dir)
    retrieved = hybrid_search(text_dir, model, question, top_k=top_k)

    cards = []
    for filename, score in retrieved:
        text = texts[filenames.index(filename)]
        cards.append({
            "filename": filename,
            "score": float(score),
            "date": report_date(filename),
            "report_number": report_number(filename),
            "snippet": best_snippet(text, question),
            "why": why_it_matters(text, question),
            "terms": matched_terms(text, question),
            "full_text": text,
        })

    answer = None
    generated = False
    ollama_message = None
    prompt = None
    if generate:
        if ollama_available():
            # Feed the model a *focused* window of each retrieved report
            # (a wide snippet around the match) rather than the whole
            # noisy page of tables. That's the lesson Part II's chunking
            # teaches, applied here so the answer stays on the evidence.
            # Chapter 5's build_prompt is still what assembles the prompt.
            focused = [best_snippet(t, question, width=900) for t in texts]
            prompt = build_prompt(question, retrieved, filenames, focused)
            answer = ollama_llm_call(prompt, model=model_name)
            generated = True
        else:
            ollama_message = OLLAMA_DOWN_MESSAGE

    return {
        "query": question,
        "cards": cards,
        "answer": answer,
        "generated": generated,
        "ollama_message": ollama_message,
        "prompt": prompt,
    }
