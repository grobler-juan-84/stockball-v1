"""SQLAlchemy ORM models for MoneyBall DB."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from moneyball.db import Base


class TradingDay(Base):
    """Core calendar spine: one row per valid market trading day."""

    __tablename__ = "trading_days"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    weekday: Mapped[str] = mapped_column(String, nullable=False)
    month: Mapped[str] = mapped_column(String, nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False)
    week_of_year: Mapped[int] = mapped_column(Integer, nullable=False)
    trading_day_of_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trading_day_of_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    days_to_month_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_month_end: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_quarter_end: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_year_end: Mapped[bool] = mapped_column(Boolean, nullable=False)
    prev_trading_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_trading_date: Mapped[date | None] = mapped_column(Date, nullable=True)
