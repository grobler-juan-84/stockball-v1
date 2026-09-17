# MoneyBall DB — Data Sources

**Purpose:** Record the authoritative data sources used to build MoneyBall DB.

Source decisions should remain simple, reproducible, and replaceable if a better source is identified.

## Source Registry

| Dataset / Table     | Source                      | Reference              | Historical Range        | Status      |
| ------------------- | --------------------------- | ---------------------- | ----------------------- | ----------- |
| `trading_days`      | pandas_market_calendars     | NYSE (`NYSE`)          | 1957-01-01 → Present    | Locked V2   |
| `daily_market_data` | TBD                         | TBD                    | TBD                     | Researching |
| `market_outcomes`   | Derived                     | `daily_market_data`    | Same as market data     | Planned     |
| `asset_regimes`     | Derived                     | `daily_market_data`    | Same as market data     | Planned     |
| `macro_conditions`  | TBD                         | TBD                    | TBD                     | Researching |
| `scheduled_events`  | TBD                         | TBD                    | TBD                     | Researching |
| `calendar_context`  | TBD / Derived               | TBD                    | TBD                     | Researching |

## Locked Decisions

### Trading Calendar — V2

MoneyBall DB V2 uses the **NYSE session calendar** from `pandas_market_calendars` as its trading-day reference.

* **Calendar:** `NYSE`
* **Start date:** 1957-01-01 (first session on or after this date; historically `1957-01-02`)
* A date returned by the NYSE calendar is considered a valid trading day.
* Remaining `trading_days` fields are derived internally from the ordered session list.
* Counters (`trading_day_of_month`, `trading_day_of_year`) are fully populated for the entire range.

#### Package selection note

`exchange_calendars` (`XNYS`) was evaluated first. It failed 1950s holiday sanity checks (e.g. New Year's Day / Christmas marked as sessions). `pandas_market_calendars` NYSE calendar passed those checks through 1957 and is therefore Locked V2.

Tiingo remains available as a price-data provider candidate and is **not** the calendar spine.

### Trading Calendar — V1 (superseded)

V1 used Tiingo SPY daily dates from 1993-01-29 with partial-history null counters for early SPY listing gaps. Replaced by V2.
