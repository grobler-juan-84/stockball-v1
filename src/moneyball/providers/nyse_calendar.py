"""NYSE session calendar via pandas_market_calendars.

Authoritative source for MoneyBall DB trading_days from 1957-01-01 onward.

Note: exchange_calendars XNYS was evaluated first but fails basic US holiday
checks in the late 1950s (e.g. New Year's Day / Christmas marked as sessions).
pandas_market_calendars NYSE calendar passes those checks back through 1957.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pandas as pd
import pandas_market_calendars as mcal

NYSE_CALENDAR_CODE = "NYSE"
NYSE_CALENDAR_START = date(1957, 1, 1)


class NyseCalendarError(RuntimeError):
    """Raised when NYSE session calendar data cannot be produced."""


def fetch_nyse_sessions(
    *,
    start_date: date = NYSE_CALENDAR_START,
    end_date: date | None = None,
) -> list[date]:
    """
    Return ordered NYSE trading sessions in ``[start_date, end_date]``.

    If ``end_date`` is omitted, use today's UTC calendar date (no far-future sessions).
    """
    if end_date is None:
        end_date = datetime.now(timezone.utc).date()
    if end_date < start_date:
        raise NyseCalendarError(
            f"end_date {end_date.isoformat()} is before start_date "
            f"{start_date.isoformat()}."
        )

    try:
        calendar = mcal.get_calendar(NYSE_CALENDAR_CODE)
        sessions = calendar.valid_days(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
    except Exception as exc:  # noqa: BLE001 — surface package failures clearly
        raise NyseCalendarError(
            f"Failed to fetch NYSE sessions "
            f"[{start_date.isoformat()} -> {end_date.isoformat()}]: {exc}"
        ) from exc

    dates = [pd.Timestamp(ts).date() for ts in sessions]
    if not dates:
        raise NyseCalendarError(
            f"No NYSE sessions in range "
            f"[{start_date.isoformat()} -> {end_date.isoformat()}]."
        )
    if dates != sorted(dates):
        raise NyseCalendarError("NYSE sessions are not chronologically sorted.")
    if len(dates) != len(set(dates)):
        raise NyseCalendarError("NYSE sessions contain duplicate dates.")
    if dates[0] < start_date:
        raise NyseCalendarError(
            f"Earliest session {dates[0].isoformat()} is before requested start "
            f"{start_date.isoformat()}."
        )
    if dates[-1] > end_date:
        raise NyseCalendarError(
            f"Latest session {dates[-1].isoformat()} is after requested end "
            f"{end_date.isoformat()}."
        )
    return dates
