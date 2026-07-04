"""Tests for code/chapter_12/torque_trend_check.py."""

import pytest


def test_torque_trend_matches_the_real_report_headers():
    from torque_trend_check import torque_trend

    # Real TORQUE header values from reports #36-38.
    readings = [("2020-11-24", 4400), ("2020-11-25", 4200), ("2020-11-26", 5615)]
    trend = torque_trend(readings)

    assert trend[0][0] == "2020-11-25"
    assert trend[0][1] == 4200
    assert trend[0][2] == pytest.approx(-0.0454545, rel=1e-3)

    assert trend[1][0] == "2020-11-26"
    assert trend[1][1] == 5615
    assert trend[1][2] == pytest.approx(0.3369047, rel=1e-3)
