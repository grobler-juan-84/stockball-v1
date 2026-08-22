# MoneyBall DB — Schema

**Version:** 1  
**Date:** 2026-08-22  
**Source:** dbdiagram.io design (planning documentation)  

> PostgreSQL migrations in Git remain authoritative once created. This document records the Version 1 conceptual schema.

---

## Overview

MoneyBall DB Version 1 is organized around a **trading-day spine** (`trading_days`). Most research tables attach to that calendar by date (and, where relevant, by symbol).

| Table | Grain | Role |
| ----- | ----- | ---- |
| `trading_days` | one row per trading day | Core calendar spine |
| `daily_market_data` | date × symbol | Prices + same-day derived market behavior |
| `market_outcomes` | date × symbol | Forward returns and outcome flags |
| `asset_regimes` | date × symbol | Trend / momentum / volatility regimes |
| `macro_conditions` | one row per trading day | Macro / monetary context (no look-ahead) |
| `scheduled_events` | one row per event | Known scheduled market-relevant events |
| `calendar_context` | one row per trading day | Holidays, transitions, seasonal calendar flags |

---

## Relationships

```
trading_days.date  <——  daily_market_data.date
trading_days.date  <——  market_outcomes.date
trading_days.date  <——  asset_regimes.date
trading_days.date  <——  macro_conditions.date
trading_days.date  <——  scheduled_events.event_date
trading_days.date  <——  calendar_context.date
```

All foreign keys reference `trading_days.date`.

---

## Tables

### `trading_days`

Core calendar spine of MoneyBall DB. One row represents one valid market trading day.

| Column | Type | Notes |
| ------ | ---- | ----- |
| `date` | date | **Primary key** |
| `weekday` | varchar | |
| `month` | varchar | |
| `quarter` | int | |
| `year` | int | |
| `day_of_month` | int | |
| `week_of_year` | int | |
| `trading_day_of_month` | int | |
| `trading_day_of_year` | int | |
| `days_to_month_end` | int | |
| `is_month_end` | boolean | |
| `is_quarter_end` | boolean | |
| `is_year_end` | boolean | |
| `prev_trading_date` | date | |
| `next_trading_date` | date | |

---

### `daily_market_data`

Daily price and derived market behavior for each symbol on each trading day.

**Primary key:** `(date, symbol)`  
**Foreign key:** `date` → `trading_days.date`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `date` | date | not null |
| `symbol` | varchar | not null |
| `open` | decimal | observed |
| `high` | decimal | observed |
| `low` | decimal | observed |
| `close` | decimal | observed |
| `volume` | bigint | observed |
| `return_1d` | decimal | derived |
| `gap_pct` | decimal | derived |
| `intraday_return` | decimal | derived |
| `range_pct` | decimal | derived |
| `drawdown_from_high` | decimal | derived |

---

### `market_outcomes`

Forward market outcomes for each symbol from a given trading date.

**Primary key:** `(date, symbol)`  
**Foreign key:** `date` → `trading_days.date`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `date` | date | not null |
| `symbol` | varchar | not null |
| `return_1d` | decimal | derived |
| `return_3d` | decimal | derived |
| `return_5d` | decimal | derived |
| `return_10d` | decimal | derived |
| `return_20d` | decimal | derived |
| `max_up_5d` | decimal | derived |
| `max_down_5d` | decimal | derived |
| `max_up_20d` | decimal | derived |
| `max_down_20d` | decimal | derived |
| `positive_1d` | boolean | derived |
| `positive_5d` | boolean | derived |
| `positive_20d` | boolean | derived |

---

### `asset_regimes`

Historical regime and market-state characteristics of each tradable asset on each trading date.

**Primary key:** `(date, symbol)`  
**Foreign key:** `date` → `trading_days.date`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `date` | date | not null |
| `symbol` | varchar | not null |
| `asset_type` | varchar | |
| `return_5d` | decimal | derived |
| `return_20d` | decimal | derived |
| `return_60d` | decimal | derived |
| `above_20dma` | boolean | derived |
| `above_50dma` | boolean | derived |
| `above_200dma` | boolean | derived |
| `distance_20dma_pct` | decimal | derived |
| `distance_50dma_pct` | decimal | derived |
| `distance_200dma_pct` | decimal | derived |
| `volatility_20d` | decimal | derived |
| `drawdown_pct` | decimal | derived |
| `trend_regime` | varchar | derived |
| `momentum_regime` | varchar | derived |
| `volatility_regime` | varchar | derived |

---

### `macro_conditions`

Macroeconomic and monetary conditions known as of each trading day. Values reflect the latest publicly available information **without look-ahead bias**.

**Primary key:** `date`  
**Foreign key:** `date` → `trading_days.date`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `date` | date | **Primary key** |
| `inflation_rate` | decimal | |
| `core_inflation_rate` | decimal | |
| `unemployment_rate` | decimal | |
| `jobless_claims` | bigint | |
| `fed_funds_rate` | decimal | |
| `treasury_2y_yield` | decimal | |
| `treasury_10y_yield` | decimal | |
| `yield_curve_10y_2y` | decimal | |
| `fed_balance_sheet` | decimal | |
| `credit_spread` | decimal | |
| `pmi` | decimal | |
| `inflation_regime` | varchar | derived |
| `rate_regime` | varchar | derived |

---

### `scheduled_events`

Scheduled market-relevant events. One row represents one known event, allowing examination of market behavior before, during, and after scheduled events.

**Primary key:** `event_id`  
**Foreign key:** `event_date` → `trading_days.date`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `event_id` | bigint | **Primary key** |
| `event_date` | date | not null |
| `event_type` | varchar | not null |
| `event_name` | varchar | not null |
| `event_category` | varchar | not null |
| `event_time` | time | |
| `release_session` | varchar | |
| `reference_period` | varchar | |
| `source` | varchar | |
| `country` | varchar | not null |

---

### `calendar_context`

Recurring calendar context and special calendar conditions for each trading day — seasonal, holiday, transition, election, tax, and payroll-related effects.

**Primary key:** `date`  
**Foreign key:** `date` → `trading_days.date`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `date` | date | **Primary key** |
| `is_day_before_holiday` | boolean | |
| `is_day_after_holiday` | boolean | |
| `holiday_name` | varchar | |
| `holiday_type` | varchar | |
| `is_shortened_trading_day` | boolean | |
| `is_shortened_week` | boolean | |
| `trading_days_in_week` | int | |
| `is_turn_of_month` | boolean | |
| `days_to_tax_deadline` | int | |
| `is_quarter_transition` | boolean | |
| `is_year_transition` | boolean | |
| `is_election_period` | boolean | |
| `is_payday_period` | boolean | |

---

## Appendix — dbdiagram.io source (v1)

```dbml
Table trading_days {
  date date [pk]

  weekday varchar
  month varchar
  quarter int
  year int
  day_of_month int
  week_of_year int

  trading_day_of_month int
  trading_day_of_year int
  days_to_month_end int

  is_month_end boolean
  is_quarter_end boolean
  is_year_end boolean

  prev_trading_date date
  next_trading_date date

  Note: 'Core calendar spine of MoneyBall DB. One row represents one valid market trading day.'
}

Table daily_market_data {
  date date [not null]
  symbol varchar [not null]

  open decimal
  high decimal
  low decimal
  close decimal
  volume bigint

  return_1d decimal
  gap_pct decimal
  intraday_return decimal
  range_pct decimal
  drawdown_from_high decimal

  indexes {
    (date, symbol) [pk]
  }

  Note: 'Daily price and derived market behavior for each symbol on each trading day.'
}

Ref: daily_market_data.date > trading_days.date

Table market_outcomes {
  date date [not null]
  symbol varchar [not null]

  return_1d decimal
  return_3d decimal
  return_5d decimal
  return_10d decimal
  return_20d decimal

  max_up_5d decimal
  max_down_5d decimal
  max_up_20d decimal
  max_down_20d decimal

  positive_1d boolean
  positive_5d boolean
  positive_20d boolean

  indexes {
    (date, symbol) [pk]
  }

  Note: 'Forward market outcomes for each symbol from a given trading date.'
}

Ref: market_outcomes.date > trading_days.date

Table asset_regimes {
  date date [not null]
  symbol varchar [not null]

  asset_type varchar

  return_5d decimal
  return_20d decimal
  return_60d decimal

  above_20dma boolean
  above_50dma boolean
  above_200dma boolean

  distance_20dma_pct decimal
  distance_50dma_pct decimal
  distance_200dma_pct decimal

  volatility_20d decimal
  drawdown_pct decimal

  trend_regime varchar
  momentum_regime varchar
  volatility_regime varchar

  indexes {
    (date, symbol) [pk]
  }

  Note: 'Historical regime and market-state characteristics of each tradable asset on each trading date.'
}

Ref: asset_regimes.date > trading_days.date

Table macro_conditions {
  date date [pk]

  inflation_rate decimal
  core_inflation_rate decimal

  unemployment_rate decimal
  jobless_claims bigint

  fed_funds_rate decimal
  treasury_2y_yield decimal
  treasury_10y_yield decimal
  yield_curve_10y_2y decimal

  fed_balance_sheet decimal

  credit_spread decimal
  pmi decimal

  inflation_regime varchar
  rate_regime varchar

  Note: 'Macroeconomic and monetary conditions known as of each trading day. Values reflect the latest publicly available information without look-ahead bias.'
}

Ref: macro_conditions.date > trading_days.date

Table scheduled_events {
  event_id bigint [pk]

  event_date date [not null]
  event_type varchar [not null]
  event_name varchar [not null]
  event_category varchar [not null]

  event_time time
  release_session varchar

  reference_period varchar

  source varchar
  country varchar [not null]

  Note: 'Scheduled market-relevant events. One row represents one known event, allowing MoneyBall DB to examine market behavior before, during, and after scheduled events.'
}

Ref: scheduled_events.event_date > trading_days.date

Table calendar_context {
  date date [pk]

  is_day_before_holiday boolean
  is_day_after_holiday boolean
  holiday_name varchar
  holiday_type varchar

  is_shortened_trading_day boolean
  is_shortened_week boolean
  trading_days_in_week int

  is_turn_of_month boolean
  days_to_tax_deadline int

  is_quarter_transition boolean
  is_year_transition boolean

  is_election_period boolean
  is_payday_period boolean

  Note: 'Recurring calendar context and special calendar conditions for each trading day, used to test seasonal, holiday, transition, election, tax, and payroll-related market effects.'
}

Ref: calendar_context.date > trading_days.date
```
