"""Chapter 12: check a structured header field's day-over-day trend.

Usage:
    python code/chapter_12/torque_trend_check.py
"""


def torque_trend(readings: list[tuple[str, float]]) -> list[tuple[str, float, float]]:
    """Given [(date, torque_value), ...] in chronological order, return
    each day's percentage change from the previous day.

    zip(readings, readings[1:]) pairs each reading with the one right
    after it -- a common Python idiom for "compare each item to its
    predecessor" without an explicit index.
    """
    trend = []
    for (_prev_date, prev_val), (date, val) in zip(readings, readings[1:]):
        pct_change = (val - prev_val) / prev_val if prev_val else 0.0
        trend.append((date, val, pct_change))
    return trend


if __name__ == "__main__":
    # Real TORQUE header values from reports #36-38 -- flat for two days,
    # then a sharp jump on the day the assembly became stuck.
    readings = [
        ("2020-11-24", 4400),
        ("2020-11-25", 4200),
        ("2020-11-26", 5615),
    ]
    for date, val, pct in torque_trend(readings):
        print(f"{date}: {val} ({pct:+.1%})")
