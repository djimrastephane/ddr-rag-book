"""Tests for the DDR RAG Companion App (book/app/).

Fast tests cover the pure text helpers and that the Streamlit module
imports without launching anything. Slow tests exercise the real
retrieval pipeline (they load the embedding model).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import helpers  # noqa: E402


def test_report_date_reads_the_filename():
    assert helpers.report_date("FORGE-16A-78-32_Drilling_050_2020-12-08.txt") == "2020-12-08"
    assert helpers.report_date("no_date_here.txt") is None


def test_best_snippet_prefers_the_window_covering_most_query_words():
    # 'pipe' appears first in a 'Drill Pipe' table row; the useful window
    # is the later one where 'stuck' and 'pipe' sit together.
    text = ("PUMP MODEL LINER Drill Pipe-5 HWDP 3787 tables numbers here and there "
            "During the slide lost tool face and became assembly became stuck "
            "Work pipe circulate lube sweep Pipe free")
    snippet = helpers.best_snippet(text, "stuck pipe event", width=120)
    assert "stuck" in snippet.lower()


def test_matched_terms_are_derived_not_invented():
    text = "the crew set packers and began fishing operations"
    terms = helpers.matched_terms(text, "packer fishing helicopter")
    assert "packer" in terms and "fishing" in terms
    assert "helicopter" not in terms  # not in the text, so not claimed


def test_why_it_matters_is_none_without_literal_overlap():
    assert helpers.why_it_matters("casing and mud tables", "weather delay") is None


def test_ollama_available_returns_a_bool_and_never_raises():
    # Point at a dead port; must report False, not crash.
    assert helpers.ollama_available("http://localhost:1") is False


def test_streamlit_app_imports_without_launching_ui():
    pytest.importorskip("streamlit")
    import streamlit_app  # guarded by __main__, so no UI render / model load
    assert hasattr(streamlit_app, "main")
    assert len(streamlit_app.SAMPLE_QUESTIONS) >= 3


def test_ensure_text_dir_rebuilds_from_sample_pdfs(tmp_path):
    # The text folder is gitignored/generated; the app must rebuild it from
    # the committed sample PDFs on a clean checkout (the bug CI caught).
    out = helpers.ensure_text_dir(tmp_path / "ddr_text")
    txts = list(out.glob("*.txt"))
    assert len(txts) == 10  # one per sample PDF
    assert any("became stuck" in p.read_text(encoding="utf-8").lower() for p in txts)


@pytest.fixture(scope="module")
def model():
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, device="cpu")


@pytest.mark.slow
def test_run_query_returns_evidence_cards_with_filenames(model, extracted_sample_text_dir):
    result = helpers.run_query(
        "What led to the fishing operation on report #50?",
        model, text_dir=extracted_sample_text_dir, top_k=3, generate=False,
    )
    assert result["cards"], "expected retrieved evidence"
    for card in result["cards"]:
        assert card["filename"].endswith(".txt")
        assert isinstance(card["score"], float)
        assert card["snippet"]
    # generate=False -> retrieval only, the answer must never be fabricated
    assert result["answer"] is None
    assert result["generated"] is False


@pytest.mark.slow
def test_run_query_handles_missing_ollama_gracefully(model, extracted_sample_text_dir, monkeypatch):
    monkeypatch.setattr(helpers, "ollama_available", lambda host=helpers.OLLAMA_HOST: False)

    result = helpers.run_query(
        "Which reports mention high torque?",
        model, text_dir=extracted_sample_text_dir, top_k=3, generate=True,
    )
    # Retrieval still works; generation degrades to a clear message.
    assert result["cards"]
    assert result["answer"] is None
    assert result["generated"] is False
    assert result["ollama_message"] == helpers.OLLAMA_DOWN_MESSAGE
