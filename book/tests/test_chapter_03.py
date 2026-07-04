"""Tests for code/chapter_03/keyword_search.py against real extracted text."""


def test_tokenize_lowercases_and_strips_punctuation():
    from keyword_search import tokenize

    tokens = tokenize("Mud fluids seepage losses in six hours 9 bbls.")

    assert "losses" in tokens
    assert "9" in tokens


def test_search_finds_only_report_038_for_stuck(extracted_sample_text_dir):
    from keyword_search import build_index, search

    index = build_index(extracted_sample_text_dir)
    results = search(index, "stuck")

    assert results == {"FORGE-16A-78-32_Drilling_038_2020-11-26.txt"}
