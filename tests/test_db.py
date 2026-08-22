"""Tests for SQLAlchemy base infrastructure (no live database required)."""

from __future__ import annotations

from moneyball.db import Base
from moneyball.db.models import TradingDay


def test_declarative_base_metadata_includes_trading_days() -> None:
    assert Base.metadata is not None
    assert "trading_days" in Base.metadata.tables
    table = Base.metadata.tables["trading_days"]
    assert list(table.primary_key.columns.keys()) == ["date"]
    assert TradingDay.__tablename__ == "trading_days"
