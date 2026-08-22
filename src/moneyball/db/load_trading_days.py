"""Load derived trading_days rows into PostgreSQL (idempotent upsert)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from moneyball.db import session_scope
from moneyball.db.models import TradingDay
from moneyball.transforms.trading_days import TRADING_DAYS_COLUMNS

# PostgreSQL binds are capped at 65535 params; 15 columns → keep batches modest.
UPSERT_BATCH_SIZE = 1000


def _row_to_record(row: pd.Series) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for col in TRADING_DAYS_COLUMNS:
        value = row[col]
        if value is None or (isinstance(value, float) and pd.isna(value)):
            record[col] = None
        else:
            record[col] = value
    return record


def upsert_trading_days(frame: pd.DataFrame) -> int:
    """
    Upsert validated trading_days rows.

    Uses PostgreSQL ``ON CONFLICT (date) DO UPDATE`` so reruns are idempotent.
    Returns the number of rows submitted for upsert.
    """
    if list(frame.columns) != TRADING_DAYS_COLUMNS:
        raise ValueError(
            f"Unexpected trading_days columns: {list(frame.columns)}"
        )
    if frame.empty:
        return 0

    records = [_row_to_record(frame.iloc[i]) for i in range(len(frame))]
    update_cols = [c for c in TRADING_DAYS_COLUMNS if c != "date"]

    with session_scope() as session:
        for start in range(0, len(records), UPSERT_BATCH_SIZE):
            batch = records[start : start + UPSERT_BATCH_SIZE]
            stmt = insert(TradingDay).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=[TradingDay.date],
                set_={col: stmt.excluded[col] for col in update_cols},
            )
            session.execute(stmt)

    return len(records)
