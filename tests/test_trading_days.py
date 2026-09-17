"""Unit tests for trading_days derivation (no live calendar API / PostgreSQL)."""

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
    assert list(frame["trading_day_of_year"]) == [1, 2, 3, 4, 5]
    assert list(frame["is_month_end"]) == [False, False, True, False, False]
    assert list(frame["days_to_month_end"]) == [2, 1, 0, None, None]
    assert frame.iloc[-1]["is_quarter_end"] == False
    assert frame.iloc[-1]["is_year_end"] == False
    assert frame.iloc[0]["prev_trading_date"] is None
    assert frame.iloc[-1]["next_trading_date"] is None

    result = validate_trading_days(frame)
    assert result.passed, result.failures


def test_mid_month_cutoff_does_not_fake_period_ends() -> None:
    dates = [
        date(2026, 6, 30),
        date(2026, 7, 1),
        date(2026, 7, 31),
        date(2026, 8, 3),
        date(2026, 8, 21),
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


def test_1957_start_counters_fully_populated() -> None:
    # Full calendar spine starting Jan 1957 — no SPY-style partial-history nulls.
    dates = [
        date(1957, 1, 2),
        date(1957, 1, 3),
        date(1957, 1, 31),
        date(1957, 2, 1),
        date(1957, 2, 4),
    ]
    frame = derive_trading_days(dates)
    assert list(frame["trading_day_of_month"]) == [1, 2, 3, 1, 2]
    assert list(frame["trading_day_of_year"]) == [1, 2, 3, 4, 5]
    assert frame.iloc[0]["is_month_end"] == False
    assert frame.iloc[2]["is_month_end"] == True
    assert frame.iloc[2]["days_to_month_end"] == 0
    result = validate_trading_days(frame)
    assert result.passed, result.failures


def test_period_end_requires_next_day_evidence() -> None:
    dates = [date(1993, 1, 29), date(1993, 2, 1), date(1993, 2, 2)]
    frame = derive_trading_days(dates)
    jan = frame.iloc[0]
    assert jan["is_month_end"] == True
    assert jan["days_to_month_end"] == 0
    assert jan["trading_day_of_month"] == 1
    assert jan["trading_day_of_year"] == 1
    assert list(frame.loc[frame["month"] == "February", "trading_day_of_month"]) == [
        1,
        2,
    ]
    result = validate_trading_days(frame)
    assert result.passed, result.failures
