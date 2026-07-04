"""Chapter 5: first RAG system -- retrieve, then generate, with citations.

Usage:
    python code/chapter_05/first_rag.py "What led to the fishing operation on report 50?"
"""

import sys
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
    verify retrieval and prompt assembly before spending an API call."""
    return prompt


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


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    if not text_dir.exists():
        raise SystemExit(f"{text_dir} does not exist -- run Chapter 1's batch extraction first.")

    question = " ".join(sys.argv[1:]) or "What led to the fishing operation on report 50?"
    model = SentenceTransformer(MODEL_NAME)
    filenames, texts = load_chunks(text_dir)
    embeddings = embed_texts(model, texts)

    _answer, evidence = answer_question(question, model, filenames, texts, embeddings, stub_llm_call, top_k=3)
    print(f"Question: {question!r}")
    print("Evidence:")
    for name in evidence:
        print(f"  {name}")
