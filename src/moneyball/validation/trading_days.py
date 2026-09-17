"""Validate a derived MoneyBall DB `trading_days` DataFrame."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from moneyball.transforms.trading_days import TRADING_DAYS_COLUMNS

# Always-required non-null fields (period distances / adjacency links may be null).
REQUIRED_NON_NULL = [
    c
    for c in TRADING_DAYS_COLUMNS
    if c
    not in {
        "prev_trading_date",
        "next_trading_date",
        "days_to_month_end",
    }
]


@dataclass
class TradingDaysValidationResult:
    """Structured validation outcome for reporting."""

    passed: bool
    total_rows: int
    earliest_date: date | None
    latest_date: date | None
    duplicate_dates: bool
    chronologically_sorted: bool
    nulls_in_required_fields: dict[str, int]
    prev_next_ok: bool
    days_to_month_end_ok: bool
    trading_day_of_month_resets_ok: bool
    trading_day_of_year_resets_ok: bool
    established_months_single_month_end: bool
    incomplete_months_have_null_days_to_end: bool
    no_fake_boundary_flags_at_cutoff: bool
    completed_quarters_single_quarter_end: bool
    completed_years_single_year_end: bool
    sample_month_bounds: list[dict[str, object]] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


def _quarter(d: date) -> int:
    return (d.month - 1) // 3 + 1


def _is_na(value: object) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def validate_trading_days(frame: pd.DataFrame) -> TradingDaysValidationResult:
    """Run structural checks on a derived ``trading_days`` dataset."""
    failures: list[str] = []

    if list(frame.columns) != TRADING_DAYS_COLUMNS:
        failures.append(
            f"Unexpected columns: {list(frame.columns)} "
            f"(expected {TRADING_DAYS_COLUMNS})"
        )

    empty = TradingDaysValidationResult(
        passed=False,
        total_rows=0,
        earliest_date=None,
        latest_date=None,
        duplicate_dates=False,
        chronologically_sorted=True,
        nulls_in_required_fields={},
        prev_next_ok=False,
        days_to_month_end_ok=False,
        trading_day_of_month_resets_ok=False,
        trading_day_of_year_resets_ok=False,
        established_months_single_month_end=False,
        incomplete_months_have_null_days_to_end=False,
        no_fake_boundary_flags_at_cutoff=False,
        completed_quarters_single_quarter_end=False,
        completed_years_single_year_end=False,
        failures=["Dataset is empty."],
    )

    total_rows = len(frame)
    if total_rows == 0:
        return empty

    dates = list(frame["date"])
    earliest = dates[0]
    latest = dates[-1]
    duplicate_dates = len(dates) != len(set(dates))
    chronologically_sorted = dates == sorted(dates)
    if duplicate_dates:
        failures.append("Duplicate dates found.")
    if not chronologically_sorted:
        failures.append("Dates are not chronologically sorted.")

    nulls: dict[str, int] = {}
    for col in REQUIRED_NON_NULL:
        count = int(frame[col].isna().sum())
        nulls[col] = count
        if count:
            failures.append(f"Required field {col!r} has {count} null(s).")

    prev_next_ok = True
    if frame.iloc[0]["prev_trading_date"] is not None:
        prev_next_ok = False
        failures.append("First row prev_trading_date must be null.")
    if frame.iloc[-1]["next_trading_date"] is not None:
        prev_next_ok = False
        failures.append("Last row next_trading_date must be null.")
    for i in range(1, total_rows):
        if frame.iloc[i]["prev_trading_date"] != dates[i - 1]:
            prev_next_ok = False
            failures.append(f"prev_trading_date mismatch at row {i}.")
            break
    for i in range(total_rows - 1):
        if frame.iloc[i]["next_trading_date"] != dates[i + 1]:
            prev_next_ok = False
            failures.append(f"next_trading_date mismatch at row {i}.")
            break

    ym = frame["date"].map(lambda d: (d.year, d.month))

    # Period-end flags require a following trading day that crosses the boundary.
    for i in range(total_rows):
        row = frame.iloc[i]
        d = dates[i]
        nxt = row["next_trading_date"]
        expected_month_end = (
            nxt is not None and (nxt.year, nxt.month) != (d.year, d.month)
        )
        expected_quarter_end = (
            nxt is not None and (nxt.year, _quarter(nxt)) != (d.year, _quarter(d))
        )
        expected_year_end = nxt is not None and nxt.year != d.year
        if bool(row["is_month_end"]) != expected_month_end:
            failures.append(f"is_month_end evidence mismatch at {d.isoformat()}.")
            break
        if bool(row["is_quarter_end"]) != expected_quarter_end:
            failures.append(f"is_quarter_end evidence mismatch at {d.isoformat()}.")
            break
        if bool(row["is_year_end"]) != expected_year_end:
            failures.append(f"is_year_end evidence mismatch at {d.isoformat()}.")
            break

    # Dataset cutoff must not invent period ends.
    last = frame.iloc[-1]
    no_fake_boundary = (
        last["next_trading_date"] is None
        and not bool(last["is_month_end"])
        and not bool(last["is_quarter_end"])
        and not bool(last["is_year_end"])
    )
    if not no_fake_boundary:
        failures.append(
            "Dataset cutoff row must not set month/quarter/year-end flags "
            "without a following trading day."
        )

    # First row is never a period end merely for being first; flags only via next.
    # (No extra check needed beyond evidence rule above.)

    established_months_ok = True
    incomplete_months_ok = True
    days_to_month_end_ok = True

    for key, group in frame.groupby(ym, sort=False):
        end_count = int(group["is_month_end"].sum())
        if end_count > 1:
            established_months_ok = False
            failures.append(f"Month {key} has {end_count} is_month_end flags.")
            break
        if end_count == 1:
            end_row = group.loc[group["is_month_end"]].iloc[0]
            if int(end_row["days_to_month_end"]) != 0:
                days_to_month_end_ok = False
                failures.append(
                    f"Established month-end {end_row['date']} must have "
                    "days_to_month_end=0."
                )
                break
            end_date = end_row["date"]
            end_pos = group["date"].tolist().index(end_date)
            for offset, (_, row) in enumerate(group.iterrows()):
                actual = row["days_to_month_end"]
                if _is_na(actual) or int(actual) != end_pos - offset:
                    days_to_month_end_ok = False
                    failures.append(
                        f"days_to_month_end incorrect for {row['date']} "
                        f"(expected {end_pos - offset}, got {actual})."
                    )
                    break
            if not days_to_month_end_ok:
                break
        else:
            # Incomplete month: no month-end flag; all distances null.
            if end_count != 0:
                incomplete_months_ok = False
                failures.append(f"Incomplete month {key} has unexpected end flags.")
                break
            if not group["days_to_month_end"].isna().all():
                incomplete_months_ok = False
                days_to_month_end_ok = False
                failures.append(
                    f"Incomplete month {key} must have null days_to_month_end."
                )
                break

    # Quarters / years with an established end have exactly one flag; open periods have zero.
    yq = list(zip(frame["year"].astype(int), frame["quarter"].astype(int), strict=True))
    frame_yq = frame.copy()
    frame_yq["_yq"] = yq
    quarter_ok = True
    for key, group in frame_yq.groupby("_yq", sort=False):
        count = int(group["is_quarter_end"].sum())
        if count > 1:
            quarter_ok = False
            failures.append(f"Quarter {key} has {count} is_quarter_end flags.")
            break
        established = count == 1
        last_in_group = group.iloc[-1]
        crossed = last_in_group["next_trading_date"] is not None and (
            last_in_group["next_trading_date"].year,
            _quarter(last_in_group["next_trading_date"]),
        ) != key
        if established != crossed:
            quarter_ok = False
            failures.append(
                f"Quarter {key} establishment inconsistent with next-day evidence."
            )
            break

    year_ok = True
    for year, group in frame.groupby("year", sort=False):
        count = int(group["is_year_end"].sum())
        if count > 1:
            year_ok = False
            failures.append(f"Year {year} has {count} is_year_end flags.")
            break
        last_in_group = group.iloc[-1]
        crossed = (
            last_in_group["next_trading_date"] is not None
            and last_in_group["next_trading_date"].year != int(year)
        )
        if (count == 1) != crossed:
            year_ok = False
            failures.append(
                f"Year {year} establishment inconsistent with next-day evidence."
            )
            break

    tdom_ok = True
    for key, group in frame.groupby(ym, sort=False):
        values = list(group["trading_day_of_month"])
        if any(_is_na(v) for v in values):
            tdom_ok = False
            failures.append(f"trading_day_of_month has unexpected nulls in {key}.")
            break
        expected = list(range(1, len(group) + 1))
        actual = [int(v) for v in values]
        if actual != expected:
            tdom_ok = False
            failures.append("trading_day_of_month does not reset/increment correctly.")
            break

    tdoy_ok = True
    for year, group in frame.groupby("year", sort=False):
        values = list(group["trading_day_of_year"])
        if any(_is_na(v) for v in values):
            tdoy_ok = False
            failures.append(f"trading_day_of_year has unexpected nulls in {year}.")
            break
        expected = list(range(1, len(group) + 1))
        actual = [int(v) for v in values]
        if actual != expected:
            tdoy_ok = False
            failures.append("trading_day_of_year does not reset/increment correctly.")
            break

    sample_keys = [
        (1957, 1),
        (2000, 1),
        (2020, 3),
        (2024, 12),
        (latest.year, latest.month),
    ]
    sample_bounds: list[dict[str, object]] = []
    seen: set[tuple[int, int]] = set()
    for key in sample_keys:
        if key in seen:
            continue
        seen.add(key)
        group = frame.loc[ym == key]
        if group.empty:
            continue
        last_days = group.iloc[-1]["days_to_month_end"]
        sample_bounds.append(
            {
                "year_month": f"{key[0]:04d}-{key[1]:02d}",
                "first_trading_day": group.iloc[0]["date"].isoformat(),
                "last_trading_day": group.iloc[-1]["date"].isoformat(),
                "trading_days_in_month": len(group),
                "month_end_established": bool(group["is_month_end"].any()),
                "last_is_month_end": bool(group.iloc[-1]["is_month_end"]),
                "last_days_to_month_end": (
                    None if _is_na(last_days) else int(last_days)
                ),
            }
        )

    passed = len(failures) == 0
    return TradingDaysValidationResult(
        passed=passed,
        total_rows=total_rows,
        earliest_date=earliest,
        latest_date=latest,
        duplicate_dates=duplicate_dates,
        chronologically_sorted=chronologically_sorted,
        nulls_in_required_fields=nulls,
        prev_next_ok=prev_next_ok,
        days_to_month_end_ok=days_to_month_end_ok and incomplete_months_ok,
        trading_day_of_month_resets_ok=tdom_ok,
        trading_day_of_year_resets_ok=tdoy_ok,
        established_months_single_month_end=established_months_ok,
        incomplete_months_have_null_days_to_end=incomplete_months_ok,
        no_fake_boundary_flags_at_cutoff=no_fake_boundary,
        completed_quarters_single_quarter_end=quarter_ok,
        completed_years_single_year_end=year_ok,
        sample_month_bounds=sample_bounds,
        failures=failures,
    )
