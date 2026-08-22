# MoneyBall DB — Data Sources

**Purpose:** Record the authoritative data sources used to build MoneyBall DB.

Source decisions should remain simple, reproducible, and replaceable if a better source is identified.

## Source Registry

| Dataset / Table     | Source        | Reference           | Historical Range     | Status      |
| ------------------- | ------------- | ------------------- | -------------------- | ----------- |
| `trading_days`      | Tiingo        | SPY daily data      | 1993-01-29 → Present | Locked V1   |
| `daily_market_data` | TBD           | TBD                 | TBD                  | Researching |
| `market_outcomes`   | Derived       | `daily_market_data` | Same as market data  | Planned     |
| `asset_regimes`     | Derived       | `daily_market_data` | Same as market data  | Planned     |
| `macro_conditions`  | TBD           | TBD                 | TBD                  | Researching |
| `scheduled_events`  | TBD           | TBD                 | TBD                  | Researching |
| `calendar_context`  | TBD / Derived | TBD                 | TBD                  | Researching |

## Locked Decisions

### Trading Calendar — V1

MoneyBall DB V1 uses **Tiingo SPY daily data** as its trading-day reference.

* **Reference instrument:** SPY
* **Start date:** 1993-01-29
* A date returned by Tiingo for SPY is considered a valid trading day.
* Remaining `trading_days` fields are derived internally.
* **Partial-history counters (V1):** `trading_day_of_month` is null for January 1993 and valid from February 1993; `trading_day_of_year` is null for all of 1993 and valid from 1994 onward (SPY does not cover earlier 1993 sessions).

If pre-1993 research is required later, a dedicated historical exchange-calendar source should be evaluated.
