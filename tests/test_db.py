"""Tests for SQLAlchemy base infrastructure (no live database required)."""

from __future__ import annotations

from moneyball.db import Base


def test_declarative_base_metadata_exists() -> None:
    assert Base.metadata is not None
    # No tables yet — schema will be introduced deliberately later.
    assert len(Base.metadata.tables) == 0
