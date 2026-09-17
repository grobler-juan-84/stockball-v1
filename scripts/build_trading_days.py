"""Build, validate, and load MoneyBall DB `trading_days` into PostgreSQL.

Flow: NYSE calendar -> extract sessions -> derive -> validate -> load.

Usage:
  python scripts/build_trading_days.py --replace
  python scripts/build_trading_days.py --end-date 2024-12-31 --replace
  python scripts/build_trading_days.py --skip-db
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import func, select, text

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from moneyball.config import ConfigurationError  # noqa: E402
from moneyball.db import session_scope  # noqa: E402
from moneyball.db.load_trading_days import upsert_trading_days  # noqa: E402
from moneyball.db.models import TradingDay  # noqa: E402
from moneyball.providers.nyse_calendar import (  # noqa: E402
    NYSE_CALENDAR_START,
    NyseCalendarError,
    fetch_nyse_sessions,
)
from moneyball.transforms.trading_days import derive_trading_days  # noqa: E402
from moneyball.validation.trading_days import (  # noqa: E402
    validate_trading_days,
)

VERIFY_DATES = [
    date(1957, 1, 2),
    date(1957, 1, 31),
    date(1993, 1, 29),
    date(2000, 1, 31),
    date(2020, 3, 31),
    date(2024, 12, 31),
    date(2026, 8, 21),
]


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY-MM-DD"
        ) from exc


def _fmt_row(row: pd.Series | object) -> str:
    if isinstance(row, pd.Series):
        items = row.items()
    else:
        items = ((c, getattr(row, c)) for c in TradingDay.__table__.columns.keys())
    parts = []
    for col, value in items:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            rendered = "null"
        elif isinstance(value, date):
            rendered = value.isoformat()
        else:
            rendered = str(value)
        parts.append(f"{col}={rendered}")
    return " | ".join(parts)


def _print_db_verification() -> None:
    print("\n=== PostgreSQL verification ===")
    with session_scope() as session:
        total = session.scalar(select(func.count()).select_from(TradingDay))
        earliest = session.scalar(select(func.min(TradingDay.date)))
        latest = session.scalar(select(func.max(TradingDay.date)))
        dupes = session.execute(
            text(
                """
                SELECT COUNT(*) FROM (
                    SELECT date FROM trading_days GROUP BY date HAVING COUNT(*) > 1
                ) d
                """
            )
        ).scalar_one()
        null_tdom_1993 = session.execute(
            text(
                """
                SELECT COUNT(*) FROM trading_days
                WHERE year = 1993 AND trading_day_of_month IS NULL
                """
            )
        ).scalar_one()
        null_tdoy_1993 = session.execute(
            text(
                """
                SELECT COUNT(*) FROM trading_days
                WHERE year = 1993 AND trading_day_of_year IS NULL
                """
            )
        ).scalar_one()

        print(f"Total rows:          {total}")
        print(f"Earliest date:       {earliest}")
        print(f"Latest date:         {latest}")
        print(f"Duplicate PK groups: {dupes}")
        print(f"1993 null tdom rows: {null_tdom_1993}")
        print(f"1993 null tdoy rows: {null_tdoy_1993}")

        first5 = session.scalars(
            select(TradingDay).order_by(TradingDay.date.asc()).limit(5)
        ).all()
        last5 = list(
            reversed(
                session.scalars(
                    select(TradingDay).order_by(TradingDay.date.desc()).limit(5)
                ).all()
            )
        )

        print("\n--- First 5 rows ---")
        for row in first5:
            print(_fmt_row(row))
        print("\n--- Last 5 rows ---")
        for row in last5:
            print(_fmt_row(row))

        print("\n--- Representative DB rows ---")
        for target in VERIFY_DATES:
            row = session.get(TradingDay, target)
            if row is None:
                print(f"{target.isoformat()}: MISSING")
            else:
                print(_fmt_row(row))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Derive, validate, and load MoneyBall trading_days from NYSE calendar."
    )
    parser.add_argument(
        "--end-date",
        type=_parse_date,
        default=None,
        help="Inclusive data cutoff (YYYY-MM-DD). Omit for today UTC.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="TRUNCATE trading_days before load so the table matches the dataset.",
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Derive and validate only; do not write to PostgreSQL.",
    )
    args = parser.parse_args()

    print("=== MoneyBall trading_days build (NYSE) ===")
    print(f"Calendar start (requested): {NYSE_CALENDAR_START.isoformat()}")
    print(
        f"End date (requested):       "
        f"{args.end_date.isoformat() if args.end_date else 'today (UTC)'}"
    )
    print(f"Replace mode:               {args.replace}")

    try:
        dates = fetch_nyse_sessions(
            start_date=NYSE_CALENDAR_START,
            end_date=args.end_date,
        )
        frame = derive_trading_days(dates)
        result = validate_trading_days(frame)
    except (ConfigurationError, NyseCalendarError, ValueError) as exc:
        print(f"FAILED: {exc}")
        return 1

    print("\n--- Validation ---")
    print(f"Passed:                         {result.passed}")
    print(f"Total rows:                     {result.total_rows}")
    print(f"Earliest date:                  {result.earliest_date}")
    print(f"Latest date:                    {result.latest_date}")
    if result.failures:
        print("\n--- Failures ---")
        for failure in result.failures:
            print(f"- {failure}")
        return 1

    print("\n--- Focus derived rows ---")
    for target in (date(1957, 1, 2), date(1993, 1, 29), frame.iloc[-1]["date"]):
        match = frame.loc[frame["date"] == target]
        if not match.empty:
            print(_fmt_row(match.iloc[0]))

    if args.skip_db:
        print("\nSkipping PostgreSQL write (--skip-db).")
        return 0

    if not args.replace:
        print(
            "\nRefusing to write without --replace after calendar source change. "
            "Pass --replace to TRUNCATE trading_days and reload."
        )
        return 1

    try:
        written = upsert_trading_days(frame, replace=True)
        print(f"\nReplaced + upserted rows:      {written}")
        _print_db_verification()
    except Exception as exc:
        print(f"DATABASE FAILED: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
