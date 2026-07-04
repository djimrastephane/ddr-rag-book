"""Tests for code/chapter_05/first_rag.py."""

import pytest


def test_build_prompt_includes_evidence_and_question():
    from first_rag import build_prompt

    retrieved = [("report_a.txt", 0.9)]
    filenames = ["report_a.txt"]
    texts = ["some report text"]

    prompt = build_prompt("What happened?", retrieved, filenames, texts)

    assert "[report_a.txt]" in prompt
    assert "some report text" in prompt
    assert "What happened?" in prompt


def test_stub_llm_call_echoes_the_prompt():
    from first_rag import stub_llm_call

    assert stub_llm_call("hello") == "hello"


@pytest.mark.slow
def test_answer_question_evidence_matches_documented_field_notes(extracted_sample_text_dir):
    """device="cpu" is forced explicitly -- sentence-transformers
    otherwise auto-selects Apple's MPS backend on Apple Silicon, which
    produced meaningfully different retrieval results than CPU inference
    in an actual CI run. See test_chapter_04.py for how this was
    confirmed."""
    from first_rag import answer_question, stub_llm_call
    from semantic_search import MODEL_NAME, embed_texts, load_chunks
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME, device="cpu")
    filenames, texts = load_chunks(extracted_sample_text_dir)
    embeddings = embed_texts(model, texts)

    _answer, evidence = answer_question(
        "What led to the fishing operation on report 50?",
        model, filenames, texts, embeddings, stub_llm_call, top_k=3,
    )

    # Matches Chapter 5's own Field Notes: report #49 is retrieved, but
    # report #50 -- the report the question is literally about -- is not.
    assert any("049" in name for name in evidence)
    assert not any("050" in name for name in evidence)
