"""Chapter 5: first RAG system -- retrieve, then generate, with citations.

Generation runs on a local model through Ollama. Setup (once):

    # install Ollama from https://ollama.com, then:
    ollama pull qwen2.5:7b-instruct
    ollama serve            # leave running in another terminal

If Ollama isn't running, the pipeline still works -- retrieval and prompt
assembly run offline, and ollama_llm_call() returns a clear message
instead of crashing, so you can see exactly what the model would have been
given.

Usage:
    python code/chapter_05/first_rag.py "What led to the packers failing to set?"
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter_04"))
from semantic_search import MODEL_NAME, embed_texts, load_chunks, search  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

PROMPT_TEMPLATE = """Answer the question using ONLY the evidence below.
If the evidence doesn't contain the answer, say so — do not guess.
Cite which report each part of your answer comes from.

Evidence:
{evidence}

Question: {question}
Answer:"""


def build_prompt(question: str, retrieved: list[tuple[str, float]],
                  filenames: list[str], texts: list[str]) -> str:
    """Turn the retrieved (filename, score) pairs into the evidence block
    of the prompt, each one labelled with its source filename so the
    model -- and later, a human reading the answer -- can tell exactly
    which report each piece of evidence came from."""
    evidence_blocks = []
    for filename, _score in retrieved:
        text = texts[filenames.index(filename)]
        evidence_blocks.append(f"[{filename}]\n{text}")
    return PROMPT_TEMPLATE.format(
        evidence="\n\n".join(evidence_blocks),
        question=question,
    )


def stub_llm_call(prompt: str) -> str:
    """Stand-in for a real LLM: just echoes the evidence back, so you can
    verify retrieval and prompt assembly before wiring up generation."""
    return prompt


def ollama_llm_call(prompt: str, model: str = "qwen2.5:7b-instruct",
                    host: str = "http://localhost:11434") -> str:
    """Generate an answer with a local model served by Ollama.

    This stays provider-agnostic in spirit: it speaks Ollama's plain HTTP
    API using only the standard library, so there's no extra package to
    install and no report text ever leaves your machine. Swap `host`/`model`
    (or replace this function entirely) to point at a different local or
    hosted model. If the Ollama server isn't reachable -- not installed,
    not running, or the model isn't pulled -- it returns a clear message
    rather than crashing, so the retrieval and prompt work above is never
    lost to a missing dependency.
    """
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    request = urllib.request.Request(
        f"{host}/api/generate", data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read())["response"].strip()
    except (urllib.error.URLError, OSError) as error:
        return (
            f"[Ollama not reachable at {host}: {error}. Install it from "
            f"ollama.com, run `ollama pull {model}` then `ollama serve`, and "
            f"re-run. Retrieval and prompt assembly still worked above — only "
            f"generation was skipped.]"
        )


def answer_question(question: str, model, filenames, texts, embeddings,
                     llm_call, top_k: int = 3) -> tuple[str, list[str]]:
    """The whole RAG pipeline in four lines: retrieve, build a prompt,
    generate, and hand back the evidence list alongside the answer so a
    reader can check the two against each other -- retrieval quality is
    what you should trust, not generation fluency."""
    retrieved = search(model, question, filenames, embeddings, top_k=top_k)
    prompt = build_prompt(question, retrieved, filenames, texts)
    answer_text = llm_call(prompt)
    evidence = [filename for filename, _score in retrieved]
    return answer_text, evidence


def evidence_excerpts(evidence: list[str], filenames: list[str],
                      texts: list[str], width: int = 200) -> list[tuple[str, str]]:
    """For each retrieved report, return (filename, short excerpt) -- the
    same text the model was handed -- so a reader sees not just WHICH
    reports backed the answer but a taste of what was actually in them."""
    excerpts = []
    for name in evidence:
        text = " ".join(texts[filenames.index(name)].split())
        excerpts.append((name, text[:width]))
    return excerpts


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 1's batch extraction first.")

    question = " ".join(sys.argv[1:]) or "What led to the packers failing to set?"
    # device="cpu" pinned explicitly -- see code/chapter_04/semantic_search.py
    # for why: Apple Silicon otherwise auto-selects the MPS backend, which
    # produces meaningfully different embeddings than CPU.
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    filenames, texts = load_chunks(text_dir)
    embeddings = embed_texts(model, texts)

    # top_k=1 here: hand the model the single best-matching report. With
    # Part I's whole-document evidence, one focused report generates a
    # cleaner answer than three concatenated pages of tables -- see the
    # chapter's Field Notes for what happens when you widen this to 3.
    answer, evidence = answer_question(
        question, model, filenames, texts, embeddings, ollama_llm_call, top_k=1)

    print(f"Question: {question}\n")
    print(f"Answer:\n{answer}\n")
    print("Sources:")
    for name, excerpt in evidence_excerpts(evidence, filenames, texts):
        print(f"  {name}")
        print(f'    "{excerpt}..."')
