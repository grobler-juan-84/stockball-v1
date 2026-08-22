"""Create trading_days table.

Revision ID: 0001_trading_days
Revises:
Create Date: 2026-08-22
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_trading_days"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "trading_days",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weekday", sa.String(), nullable=False),
        sa.Column("month", sa.String(), nullable=False),
        sa.Column("quarter", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("day_of_month", sa.Integer(), nullable=False),
        sa.Column("week_of_year", sa.Integer(), nullable=False),
        sa.Column("trading_day_of_month", sa.Integer(), nullable=True),
        sa.Column("trading_day_of_year", sa.Integer(), nullable=True),
        sa.Column("days_to_month_end", sa.Integer(), nullable=True),
        sa.Column("is_month_end", sa.Boolean(), nullable=False),
        sa.Column("is_quarter_end", sa.Boolean(), nullable=False),
        sa.Column("is_year_end", sa.Boolean(), nullable=False),
        sa.Column("prev_trading_date", sa.Date(), nullable=True),
        sa.Column("next_trading_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("date"),
    )


def downgrade() -> None:
    op.drop_table("trading_days")
