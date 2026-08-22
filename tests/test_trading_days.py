"""Unit tests for trading_days derivation (no live Tiingo / PostgreSQL)."""

from __future__ import annotations

from datetime import date

from moneyball.transforms.trading_days import derive_trading_days
from moneyball.validation.trading_days import validate_trading_days


def test_established_month_and_incomplete_trailing_month() -> None:
    # January complete (next day crosses into February). February incomplete.
    dates = [
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 31),
        date(2024, 2, 1),
        date(2024, 2, 29),
    ]
    frame = derive_trading_days(dates)
    assert list(frame["trading_day_of_month"]) == [1, 2, 3, 1, 2]
    assert list(frame["is_month_end"]) == [False, False, True, False, False]
    assert list(frame["days_to_month_end"]) == [2, 1, 0, None, None]
    assert frame.iloc[-1]["is_quarter_end"] == False
    assert frame.iloc[-1]["is_year_end"] == False
    assert frame.iloc[0]["prev_trading_date"] is None
    assert frame.iloc[-1]["next_trading_date"] is None

    result = validate_trading_days(frame)
    assert result.passed, result.failures


def test_mid_month_cutoff_does_not_fake_period_ends() -> None:
    # Simulate a 2026-08-21-style cutoff mid-month / mid-quarter / mid-year.
    dates = [
        date(2026, 6, 30),  # Q2 end (next crosses to July)
        date(2026, 7, 1),
        date(2026, 7, 31),  # July month end
        date(2026, 8, 3),
        date(2026, 8, 21),  # cutoff
    ]
    frame = derive_trading_days(dates)
    cutoff = frame.iloc[-1]
    assert cutoff["date"] == date(2026, 8, 21)
    assert cutoff["is_month_end"] == False
    assert cutoff["is_quarter_end"] == False
    assert cutoff["is_year_end"] == False
    assert cutoff["days_to_month_end"] is None

    august = frame.loc[frame["month"] == "August"]
    assert not august["is_month_end"].any()
    assert august["days_to_month_end"].isna().all()

    # Established boundaries earlier in the series still work.
    assert bool(frame.loc[frame["date"] == date(2026, 6, 30), "is_quarter_end"].iloc[0])
    assert bool(frame.loc[frame["date"] == date(2026, 7, 31), "is_month_end"].iloc[0])

    result = validate_trading_days(frame)
    assert result.passed, result.failures
    assert result.no_fake_boundary_flags_at_cutoff


def test_known_historical_period_ends() -> None:
    dates = [
        date(2019, 12, 31),
        date(2020, 1, 2),
        date(2020, 3, 30),
        date(2020, 3, 31),
        date(2020, 4, 1),
        date(2020, 12, 31),
        date(2021, 1, 4),
    ]
    frame = derive_trading_days(dates)
    by_date = frame.set_index("date")

    assert bool(by_date.loc[date(2019, 12, 31), "is_year_end"])
    assert bool(by_date.loc[date(2019, 12, 31), "is_quarter_end"])
    assert bool(by_date.loc[date(2019, 12, 31), "is_month_end"])
    assert bool(by_date.loc[date(2020, 3, 31), "is_quarter_end"])
    assert bool(by_date.loc[date(2020, 3, 31), "is_month_end"])
    assert bool(by_date.loc[date(2020, 12, 31), "is_year_end"])

    result = validate_trading_days(frame)
    assert result.passed, result.failures


def test_dataset_start_uses_next_day_evidence_not_first_row_alone() -> None:
    # Only day in January, but next day is February → month-end is evidenced.
    dates = [date(1993, 1, 29), date(1993, 2, 1), date(1993, 2, 2)]
    frame = derive_trading_days(dates)
    jan = frame.iloc[0]
    assert jan["date"] == date(1993, 1, 29)
    assert jan["is_month_end"] == True
    assert jan["days_to_month_end"] == 0
    assert jan["is_quarter_end"] == False
    assert jan["is_year_end"] == False
    assert jan["trading_day_of_month"] is None
    assert jan["trading_day_of_year"] is None
    # February month counters start; year counters stay null for all of 1993.
    feb = frame.loc[frame["month"] == "February"]
    assert list(feb["trading_day_of_month"]) == [1, 2]
    assert list(feb["trading_day_of_year"]) == [None, None]
    assert list(feb["is_month_end"]) == [False, False]

    result = validate_trading_days(frame)
    assert result.passed, result.failures


def test_1993_partial_history_null_counters() -> None:
    dates = [
        date(1993, 1, 29),
        date(1993, 2, 1),
        date(1993, 2, 26),
        date(1993, 3, 1),
        date(1993, 12, 31),
        date(1994, 1, 3),
        date(1994, 1, 4),
    ]
    frame = derive_trading_days(dates)
    jan = frame.loc[frame["date"] == date(1993, 1, 29)].iloc[0]
    assert jan["trading_day_of_month"] is None
    assert jan["trading_day_of_year"] is None
    assert frame.loc[frame["date"] == date(1993, 2, 1), "trading_day_of_month"].iloc[0] == 1
    assert frame.loc[frame["date"] == date(1993, 2, 1), "trading_day_of_year"].iloc[0] is None
    assert frame.loc[frame["date"] == date(1993, 12, 31), "trading_day_of_year"].iloc[0] is None
    assert frame.loc[frame["date"] == date(1994, 1, 3), "trading_day_of_year"].iloc[0] == 1
    assert frame.loc[frame["date"] == date(1994, 1, 4), "trading_day_of_year"].iloc[0] == 2
    result = validate_trading_days(frame)
    assert result.passed, result.failures
