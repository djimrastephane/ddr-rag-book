"""Tests for code/chapter_10/traceable_answers.py."""


def test_format_evidence_lists_report_and_page():
    from traceable_answers import Citation, format_evidence

    evidence = format_evidence([Citation(report="report_038.pdf", page=1)])

    assert "report_038.pdf page 1" in evidence


def test_find_date_gaps_detects_the_real_archive_gaps():
    from traceable_answers import find_date_gaps

    sample_dates = [
        "2020-10-22", "2020-11-07", "2020-11-24", "2020-11-25",
        "2020-11-26", "2020-11-27", "2020-12-06", "2020-12-07",
        "2020-12-08", "2021-01-06",
    ]
    gaps = find_date_gaps(sample_dates)

    assert len(gaps) == 4
    # The real gap right before the Completion report, discussed in Ch.10.
    assert gaps[-1] == ("2020-12-09", "2021-01-05")
