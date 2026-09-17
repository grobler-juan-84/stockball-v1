"""Derive MoneyBall DB `trading_days` fields from an ordered trading-date list."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import pandas as pd

TRADING_DAYS_COLUMNS = [
    "date",
    "weekday",
    "month",
    "quarter",
    "year",
    "day_of_month",
    "week_of_year",
    "trading_day_of_month",
    "trading_day_of_year",
    "days_to_month_end",
    "is_month_end",
    "is_quarter_end",
    "is_year_end",
    "prev_trading_date",
    "next_trading_date",
]


def _quarter(d: date) -> int:
    return (d.month - 1) // 3 + 1


def derive_trading_days(trading_dates: Sequence[date]) -> pd.DataFrame:
    """
    Build the ``trading_days`` table from ordered exchange trading dates.

    Calendar fields (weekday, month, quarter, year, day_of_month, week_of_year)
    come from the civil calendar. Sequence fields use the trading-day list itself.

    ``week_of_year`` uses the ISO week number (``date.isocalendar().week``).

    Period-end flags are set only when the *next* trading date crosses into a new
    month / quarter / year. Dataset start/end alone never imply a period boundary.

    ``days_to_month_end`` is remaining trading days after the current date before
    the established month-end trading day. If that month-end cannot be established
    (no later trading day in a subsequent month), the value is null.
    """
    if len(trading_dates) == 0:
        raise ValueError("Cannot derive trading_days from an empty date list.")

    dates = list(trading_dates)
    if len(dates) != len(set(dates)):
        raise ValueError("Trading dates must be unique before derivation.")
    if dates != sorted(dates):
        raise ValueError(
            "Trading dates must be sorted chronologically before derivation."
        )

    n = len(dates)
    prev_dates: list[date | None] = [None, *dates[:-1]]
    next_dates: list[date | None] = [*dates[1:], None]

    is_month_end: list[bool] = []
    is_quarter_end: list[bool] = []
    is_year_end: list[bool] = []
    for i, d in enumerate(dates):
        nxt = next_dates[i]
        if nxt is None:
            is_month_end.append(False)
            is_quarter_end.append(False)
            is_year_end.append(False)
            continue
        is_month_end.append((nxt.year, nxt.month) != (d.year, d.month))
        is_quarter_end.append((nxt.year, _quarter(nxt)) != (d.year, _quarter(d)))
        is_year_end.append(nxt.year != d.year)

    month_end_index: dict[tuple[int, int], int] = {}
    for i, flag in enumerate(is_month_end):
        if flag:
            key = (dates[i].year, dates[i].month)
            month_end_index[key] = i

    days_to_month_end: list[int | None] = []
    for i, d in enumerate(dates):
        end_i = month_end_index.get((d.year, d.month))
        if end_i is None:
            days_to_month_end.append(None)
        else:
            days_to_month_end.append(end_i - i)

    trading_day_of_month: list[int] = []
    month_counters: dict[tuple[int, int], int] = {}
    for d in dates:
        key = (d.year, d.month)
        month_counters[key] = month_counters.get(key, 0) + 1
        trading_day_of_month.append(month_counters[key])

    trading_day_of_year: list[int] = []
    year_counters: dict[int, int] = {}
    for d in dates:
        year_counters[d.year] = year_counters.get(d.year, 0) + 1
        trading_day_of_year.append(year_counters[d.year])

    frame = pd.DataFrame(
        {
            "date": dates,
            "weekday": [d.strftime("%A") for d in dates],
            "month": [d.strftime("%B") for d in dates],
            "quarter": [_quarter(d) for d in dates],
            "year": [d.year for d in dates],
            "day_of_month": [d.day for d in dates],
            "week_of_year": [d.isocalendar().week for d in dates],
            "trading_day_of_month": trading_day_of_month,
            "trading_day_of_year": trading_day_of_year,
            "is_month_end": is_month_end,
            "is_quarter_end": is_quarter_end,
            "is_year_end": is_year_end,
        }
    )
    frame["days_to_month_end"] = pd.Series(days_to_month_end, dtype=object)
    frame["prev_trading_date"] = pd.Series(prev_dates, dtype=object)
    frame["next_trading_date"] = pd.Series(next_dates, dtype=object)
    assert n == len(frame)
    return frame.loc[:, TRADING_DAYS_COLUMNS].copy()
