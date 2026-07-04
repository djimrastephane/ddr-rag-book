"""Tests for code/chapter_02/expand_abbreviations.py."""


def test_expand_text_expands_known_abbreviations():
    from expand_abbreviations import expand_text

    text = "Pick up Curve assembly 2, BHA 21. WOB 20 TO 35k."
    expanded = expand_text(text)

    assert "bottom hole assembly" in expanded
    assert "weight on bit" in expanded


def test_expand_text_respects_word_boundaries():
    from expand_abbreviations import expand_text

    # "MD" must expand only as its own word -- not as a substring of "MDT".
    text = "MDT tool run, MD 6500 ft."
    expanded = expand_text(text)

    assert "MDT" in expanded
    assert "measured depth 6500 ft" in expanded
