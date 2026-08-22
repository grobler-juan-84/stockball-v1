"""Minimal Tiingo end-of-day client for MoneyBall DB.

Fetches daily price history only. Does not write to PostgreSQL.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from typing import Any

from moneyball.config import ConfigurationError, REPO_ROOT, _load_dotenv

TIINGO_EOD_URL = "https://api.tiingo.com/tiingo/daily/{ticker}/prices"
SPY_TRADING_CALENDAR_START = date(1993, 1, 29)


class TiingoError(RuntimeError):
    """Raised when a Tiingo request fails or returns unusable data."""


def get_tiingo_api_token() -> str:
    """
    Return TIINGO_API_TOKEN from the environment.

    Loads `.env` / `.env.local` via the project config helper.
    Never logs or returns a redacted form for printing — callers must not print it.
    """
    _load_dotenv()
    token = os.getenv("TIINGO_API_TOKEN", "").strip()
    if not token:
        raise ConfigurationError(
            "TIINGO_API_TOKEN is not set. "
            "Add it to .env.local (or .env) without committing the secret."
        )
    return token


def fetch_daily_prices(
    ticker: str,
    *,
    start_date: date,
    end_date: date | None = None,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch Tiingo EOD prices for ``ticker``.

    Parameters
    ----------
    ticker:
        Symbol such as ``SPY``.
    start_date:
        Inclusive start (YYYY-MM-DD).
    end_date:
        Optional inclusive cutoff. If omitted, Tiingo returns through latest available.
    token:
        Optional override; defaults to ``TIINGO_API_TOKEN``.
    """
    api_token = token if token is not None else get_tiingo_api_token()

    params: dict[str, str] = {
        "startDate": start_date.isoformat(),
        "format": "json",
    }
    if end_date is not None:
        params["endDate"] = end_date.isoformat()

    url = (
        TIINGO_EOD_URL.format(ticker=urllib.parse.quote(ticker.upper()))
        + "?"
        + urllib.parse.urlencode(params)
    )
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json",
            "User-Agent": "moneyball-db/0.1",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise TiingoError(
            f"Tiingo HTTP {exc.code} for {ticker.upper()}: {body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise TiingoError(f"Tiingo connection failed: {exc.reason}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise TiingoError("Tiingo returned malformed JSON.") from exc

    if not isinstance(data, list):
        raise TiingoError(
            f"Tiingo returned unexpected payload type: {type(data).__name__}"
        )
    if len(data) == 0:
        raise TiingoError(
            f"Tiingo returned no price rows for {ticker.upper()} "
            f"(start={start_date.isoformat()}, end={end_date.isoformat() if end_date else 'latest'})."
        )

    return data


def extract_trading_dates(price_rows: list[dict[str, Any]]) -> list[date]:
    """Normalize Tiingo price-row ``date`` fields to a list of ``date`` values."""
    dates: list[date] = []
    for i, row in enumerate(price_rows):
        if not isinstance(row, dict):
            raise TiingoError(f"Malformed price row at index {i}: expected object.")
        raw = row.get("date")
        if not raw or not isinstance(raw, str):
            raise TiingoError(f"Malformed price row at index {i}: missing date.")
        try:
            # Tiingo returns e.g. "1993-01-29T00:00:00.000Z"
            normalized = raw.replace("Z", "+00:00")
            dates.append(datetime.fromisoformat(normalized).date())
        except ValueError as exc:
            raise TiingoError(
                f"Malformed date at index {i}: {raw!r}"
            ) from exc
    return dates


# Re-export for callers that need the repo root when writing raw artifacts later.
__all__ = [
    "SPY_TRADING_CALENDAR_START",
    "TiingoError",
    "REPO_ROOT",
    "extract_trading_dates",
    "fetch_daily_prices",
    "get_tiingo_api_token",
]
