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
def test_report_049_scores_clearly_higher_than_report_050(extracted_sample_text_dir):
    from semantic_search import MODEL_NAME, embed_texts, load_chunks, search
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    filenames, texts = load_chunks(extracted_sample_text_dir)
    embeddings = embed_texts(model, texts)

    results = search(
        model, "What led to the fishing operation on report 50?",
        filenames, embeddings, top_k=len(filenames),
    )
    scores = dict(results)

    report_049 = next(name for name in scores if "049" in name)
    report_050 = next(name for name in scores if "050" in name)

    # Matches Chapter 5's own Field Notes: report #49 (packers failing to
    # set) scores meaningfully higher than report #50 -- the report the
    # question is literally about -- at whole-document granularity. This
    # checks the score relationship directly rather than exact membership
    # in a fixed top_k=3 cutoff: the book's own documented ranking has
    # report #50 sitting right at rank 7, just a hair below rank 3-6,
    # close enough that the *exact* cutoff position can shift by a rank
    # between BLAS backends even with identical code and pinned
    # dependency versions. The score gap tested here is comfortably wide.
    assert scores[report_049] > scores[report_050]
