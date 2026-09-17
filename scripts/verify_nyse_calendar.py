"""Verify NYSE calendar coverage for MoneyBall trading_days (1957+).

Uses pandas_market_calendars (selected after exchange_calendars failed
1950s holiday sanity checks). Does not modify PostgreSQL.

Usage:
  python scripts/verify_nyse_calendar.py
  python scripts/verify_nyse_calendar.py --end-date 2026-08-21
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas_market_calendars as mcal  # noqa: E402

from moneyball.providers.nyse_calendar import (  # noqa: E402
    NYSE_CALENDAR_CODE,
    NYSE_CALENDAR_START,
    NyseCalendarError,
    fetch_nyse_sessions,
)


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY-MM-DD"
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify NYSE session coverage from 1957-01-01."
    )
    parser.add_argument(
        "--end-date",
        type=_parse_date,
        default=None,
        help="Inclusive cutoff (YYYY-MM-DD). Default: today UTC.",
    )
    args = parser.parse_args()

    print("=== NYSE coverage verification ===")
    print(f"pandas_market_calendars version: {mcal.__version__}")
    print(f"Calendar code:                   {NYSE_CALENDAR_CODE}")
    print(f"Requested start:                 {NYSE_CALENDAR_START.isoformat()}")
    print(
        f"Requested end:                   "
        f"{args.end_date.isoformat() if args.end_date else 'today (UTC)'}"
    )

    try:
        dates = fetch_nyse_sessions(
            start_date=NYSE_CALENDAR_START,
            end_date=args.end_date,
        )
    except NyseCalendarError as exc:
        print(f"FAILED: {exc}")
        return 1

    date_set = set(dates)
    failures: list[str] = []
    if dates[0] < NYSE_CALENDAR_START:
        failures.append(f"Earliest session {dates[0]} precedes {NYSE_CALENDAR_START}.")
    if any(d.weekday() >= 5 for d in dates[:50]):
        failures.append("Weekend found among early sessions.")
    # Known closes / holidays that must not be sessions.
    for closed in (
        date(1957, 1, 1),
        date(1957, 7, 4),
        date(1957, 12, 25),
        date(2001, 9, 11),
        date(2001, 9, 12),
        date(2024, 1, 1),
        date(2024, 12, 25),
    ):
        if args.end_date is not None and closed > args.end_date:
            continue
        if closed < NYSE_CALENDAR_START:
            continue
        if closed in date_set:
            failures.append(f"{closed.isoformat()} unexpectedly present as a session.")

    jan_1957 = [d for d in dates if d.year == 1957 and d.month == 1]
    if not jan_1957:
        failures.append("No January 1957 sessions returned.")
    elif jan_1957[0] != date(1957, 1, 2):
        # 1957-01-01 was Tuesday New Year's Day (closed); first session should be Jan 2.
        failures.append(
            f"Expected first January 1957 session 1957-01-02, got {jan_1957[0]}."
        )

    print(f"Earliest session:                {dates[0].isoformat()}")
    print(f"Latest session:                  {dates[-1].isoformat()}")
    print(f"Total sessions:                  {len(dates)}")
    print(f"First 5 dates:                   {[d.isoformat() for d in dates[:5]]}")
    print(f"Last 5 dates:                    {[d.isoformat() for d in dates[-5:]]}")
    print(f"January 1957 sessions:           {len(jan_1957)}")
    if jan_1957:
        print(
            f"January 1957 range:              "
            f"{jan_1957[0].isoformat()} -> {jan_1957[-1].isoformat()}"
        )
    print(f"1957-01-01 is session:           {date(1957, 1, 1) in date_set}")
    print(f"2001-09-11 is session:           {date(2001, 9, 11) in date_set}")

    if failures:
        print("\n--- Failures ---")
        for item in failures:
            print(f"- {item}")
        return 1

    print("\nCoverage verification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
