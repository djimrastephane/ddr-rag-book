"""Chapter 5 challenge solution: a crude hallucination guard.

Rejects any answer that mentions a report filename (or bare report
number) that wasn't in the retrieved evidence list. This won't catch
every hallucination -- an LLM can invent a false claim about a report
that WAS legitimately retrieved -- but it catches the specific failure
mode this chapter's Field Notes warns about: a question that names a
report number the retrieval step never actually found.

Plugging in a real LLM (local via transformers/ollama, or a hosted API)
is left to you -- set `llm_call` to something that actually calls one.
This script demonstrates the guard logic itself, using the same stub
`llm_call` as the main chapter so it runs with no external dependencies
or API keys.

Usage:
    python code/chapter_05/challenge/hallucination_guard.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from first_rag import answer_question, stub_llm_call  # noqa: E402
from semantic_search import MODEL_NAME, embed_texts, load_chunks  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402


def guarded_answer(question: str, model, filenames, texts, embeddings,
                    llm_call, top_k: int = 3) -> tuple[str, list[str], bool]:
    """Returns (answer, evidence, flagged). flagged=True means the answer
    mentioned a report number not present in the retrieved evidence."""
    answer, evidence = answer_question(question, model, filenames, texts, embeddings, llm_call, top_k)

    # Filenames look like "FORGE-16A-78-32_Drilling_049_2020-12-07.txt" --
    # pull the 3-digit report number out of each retrieved filename.
    evidence_report_numbers = {
        m.group(1) for name in evidence
        for m in [re.search(r"_(\d{3})_", name)] if m
    }
    # Find every "report 50" / "report #50" style mention in the generated
    # answer text, so we can compare what the answer CLAIMS against what
    # was actually retrieved.
    mentioned_numbers = set(re.findall(r"report #?(\d{2,3})\b", answer, re.IGNORECASE))
    # normalize to 3-digit form for comparison
    mentioned_numbers = {n.zfill(3) for n in mentioned_numbers}

    # Any report number the answer mentions that wasn't actually retrieved
    # is unsupported -- the model couldn't have seen that report's content.
    unsupported = mentioned_numbers - evidence_report_numbers
    flagged = bool(unsupported)
    if flagged:
        answer = (f"[REJECTED: answer references report(s) {sorted(unsupported)} "
                   f"not present in retrieved evidence {sorted(evidence_report_numbers)}]")
    return answer, evidence, flagged


if __name__ == "__main__":
    text_dir = Path("datasets/ddr_text")
    model = SentenceTransformer(MODEL_NAME)
    filenames, texts = load_chunks(text_dir)
    embeddings = embed_texts(model, texts)

    # Case 1: a question entirely outside the ten-report archive.
    question = "What happened on report #100?"
    fake_llm = lambda prompt: "Report #100 shows the crew tripping in hole with no issues."  # noqa: E731
    answer, evidence, flagged = guarded_answer(question, model, filenames, texts, embeddings, fake_llm)
    print(f"Question: {question!r}")
    print(f"Evidence retrieved: {evidence}")
    print(f"Answer: {answer}")
    assert flagged, "expected the guard to reject a fabricated report #100 answer"
    print("Confirmed: guard correctly rejected an answer citing a report never retrieved.\n")

    # Case 2: a genuine, honest answer that only cites what was actually
    # retrieved. (The echo stub from the main chapter isn't a fair test here
    # -- it echoes the question itself, which names "report 50" regardless
    # of what got retrieved. A real LLM would only cite reports it was
    # actually shown, which is what this fake answer simulates.)
    question2 = "What led to the fishing operation on report 50?"
    honest_llm = lambda prompt: (  # noqa: E731
        "Report #49 shows packers failing to set; the crew picked up a "
        "fishing BHA the same day. Report #48 shows a ROP decrease shortly "
        "before that."
    )
    answer2, evidence2, flagged2 = guarded_answer(question2, model, filenames, texts, embeddings, honest_llm)
    print(f"Question: {question2!r}")
    print(f"Evidence retrieved: {evidence2}")
    print(f"Answer: {answer2}")
    print(f"Flagged: {flagged2}")
    assert not flagged2, "expected the guard to accept an answer that only cites retrieved reports"
    print("Confirmed: guard correctly accepted an honest, fully-grounded answer.")
