# Project Steps

Running log of work completed on MoneyBall DB. Appended after each prompt.

---

## Step 1 — Document project manifesto

Captured the MoneyBall DB research philosophy in `docs/project_manifesto.md` (data-first lab, reproducibility, observed vs derived data, validation discipline).

## Step 2 — Document initial tech stack

Captured the stack and pipeline philosophy in `docs/tech_stack.md` (Python, PostgreSQL, SQLAlchemy, Alembic, pandas, NumPy, local reproducibility; interfaces and cloud deferred).

## Step 3 — Scaffold technical foundation

Initialized the Python project layout (`src/moneyball`, scripts, migrations, data dirs), `pyproject.toml`, `.env.example`, `.gitignore`, SQLAlchemy/Alembic wiring, provider/pipeline stubs, pytest suite (4 passing), and `README.md`. No schema tables or data fetching yet.

## Step 4 — Document schema Version 1

Created `docs/db-schema.md` (v1, 2026-08-22) from the dbdiagram.io design: seven tables centered on `trading_days`, with keys/relationships and the DBML appendix. No migrations generated.

## Step 5 — Initial Git commit and GitHub push

Initialized git, tightened `.gitignore` for `.env.*` (keeping `.env.example`), committed the foundation (29 files), and pushed `main` to https://github.com/grobler-juan-84/stockball-v1.git.

## Step 6 — Add project steps backlog

Implemented the project-steps rule by creating root `project_steps.md` and backfilling Steps 1–5 from completed work (mid-stop prompts omitted). Removed empty `docs/project_steps.md` so the log lives only at the repo root as the rule specifies.

## Step 7 — Test Tiingo SPY trading-date fetch

Added minimal Tiingo client (`src/moneyball/providers/tiingo.py`) and `scripts/test_tiingo_spy_dates.py` using `TIINGO_API_TOKEN` from `.env.local`. Verified SPY daily dates from 1993-01-29 through latest (8448 dates, no duplicates, sorted). No PostgreSQL writes or calendar field derivation.

## Step 8 — Derive and validate trading_days dataset

Added `transforms/trading_days.py` and `validation/trading_days.py`, plus `scripts/build_trading_days.py` (supports `--end-date`). Built the full in-memory V1 `trading_days` table from Tiingo SPY dates (8448 rows, 1993-01-29 → 2026-08-21); validation passed. No PostgreSQL writes.

## Step 9 — Fix trading_days period-end boundary logic

Period-end flags now require next-trading-day evidence that the calendar period actually ended; dataset cutoffs no longer invent month/quarter/year ends. Incomplete months use `days_to_month_end=null`. Verified with `--end-date 2026-08-21` and updated unit tests (8 passed).

## Step 10 — Persist trading_days in PostgreSQL

Nullified January 1993 `trading_day_of_*` counters; added `TradingDay` model, Alembic migration `0001_trading_days`, and batched upsert loader. Migrated local Postgres, loaded 8448 SPY-derived rows (1993-01-29→2026-08-21), verified representatives, and confirmed idempotent rerun. No other tables.

## Step 11 — Null trading_day_of_year for all of 1993

Corrected derivation so `trading_day_of_year` is null throughout 1993 (valid from 1994); `trading_day_of_month` remains null only for January 1993. Reloaded PostgreSQL, tests updated. Marked `trading_days` V1 complete.

## Step 12 — Commit and push trading_days V1

Committed and pushed `trading_days` V1 work to GitHub (`1da1cdc`), including Tiingo fetch/derive/validate, Alembic migration, PostgreSQL upsert loader, tests, and project-steps rule. Secrets in `.env.local` were not committed.

## Step 13 — Switch trading_days to NYSE calendar V2

Replaced Tiingo SPY calendar source with `pandas_market_calendars` NYSE sessions from 1957-01-01 (after `exchange_calendars` failed 1950s holiday checks). Truncated and reloaded `trading_days`, removed SPY partial-history nulls, and updated docs/tests.
