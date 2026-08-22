"""Fetch SPY daily dates from Tiingo and print a verification report.

Does not touch PostgreSQL or derive trading_days calendar fields.

Usage:
  python scripts/test_tiingo_spy_dates.py
  python scripts/test_tiingo_spy_dates.py --end-date 2024-12-31
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

# Allow running as `python scripts/...` without requiring PYTHONPATH.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from moneyball.config import ConfigurationError  # noqa: E402
from moneyball.providers.tiingo import (  # noqa: E402
    SPY_TRADING_CALENDAR_START,
    TiingoError,
    extract_trading_dates,
    fetch_daily_prices,
)

SYMBOL = "SPY"


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY-MM-DD"
        ) from exc


def _print_report(
    *,
    success: bool,
    symbol: str,
    dates: list[date],
    end_date: date | None,
    error: str | None = None,
) -> None:
    print("=== Tiingo SPY trading-date verification ===")
    print(f"Fetch status:           {'SUCCESS' if success else 'FAILED'}")
    print(f"Symbol:                 {symbol}")
    print(f"Start date (requested): {SPY_TRADING_CALENDAR_START.isoformat()}")
    print(
        f"End date (requested):   "
        f"{end_date.isoformat() if end_date else 'latest available'}"
    )
    if error:
        print(f"Error:                  {error}")
        return

    earliest = dates[0]
    latest = dates[-1]
    first_five = dates[:5]
    last_five = dates[-5:]
    has_duplicates = len(dates) != len(set(dates))
    is_sorted = dates == sorted(dates)

    print(f"Earliest returned date: {earliest.isoformat()}")
    print(f"Latest returned date:   {latest.isoformat()}")
    print(f"Total trading dates:    {len(dates)}")
    print(f"First 5 dates:          {[d.isoformat() for d in first_five]}")
    print(f"Last 5 dates:           {[d.isoformat() for d in last_five]}")
    print(f"Duplicate dates:        {'YES' if has_duplicates else 'NO'}")
    print(f"Chronologically sorted: {'YES' if is_sorted else 'NO'}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test Tiingo SPY daily fetch and extract trading dates."
    )
    parser.add_argument(
        "--end-date",
        type=_parse_date,
        default=None,
        help="Inclusive data cutoff (YYYY-MM-DD). Omit for latest Tiingo data.",
    )
    args = parser.parse_args()

    try:
        rows = fetch_daily_prices(
            SYMBOL,
            start_date=SPY_TRADING_CALENDAR_START,
            end_date=args.end_date,
        )
        dates = extract_trading_dates(rows)
    except (ConfigurationError, TiingoError) as exc:
        _print_report(
            success=False,
            symbol=SYMBOL,
            dates=[],
            end_date=args.end_date,
            error=str(exc),
        )
        return 1

    _print_report(
        success=True,
        symbol=SYMBOL,
        dates=dates,
        end_date=args.end_date,
    )

    has_duplicates = len(dates) != len(set(dates))
    is_sorted = dates == sorted(dates)
    if has_duplicates or not is_sorted:
        print("Verification FAILED: dates must be unique and chronological.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
