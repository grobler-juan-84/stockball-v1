# Project Phases

## Phase 1 — Foundation, Architecture & Database Design

**Status:** Complete
**Completed:** 2026-08-22

### Purpose

Phase 1 established the initial foundation of MoneyBall DB.

The focus was on defining the project's purpose, choosing the initial architecture and technology stack, and designing the first version of the database.

### Completed

Three foundational documents were created and added to the project:

* `/docs/project_manifesto.md`
* `/docs/tech_stack.md`
* `/docs/db-schema.md`

These documents define the project's research philosophy, technical architecture, and initial 7-table database design.

The project was then initialized through Cursor using the planned tech stack, including Python, local PostgreSQL, SQLAlchemy, Alembic, pandas, NumPy and supporting dependencies.

### Important

Phase 1 focused on **planning and initial setup only**.

The technical environment, database connections, migrations, data pipelines and dependencies have **not yet been fully tested or validated**.

Git/GitHub has also **not yet been initialized** for the project.

Testing, validation and Git setup will be handled deliberately in later phases rather than being considered part of Phase 1.

### Phase 1 Outcome

MoneyBall DB now has:

* a defined project philosophy,
* a documented technical architecture,
* an initial Version 1 database schema,
* the three core project documents,
* and an initialized development environment.

Phase 1 therefore concludes the **planning and foundation stage** of MoneyBall DB.

---

## Phase 2 — Data Sources & Database Population

**Status:** Next

---

## Phase 2 — Data Sources & Database Population

**Status:** In Progress  
**Started:** 2026-08-22

### Purpose

Phase 2 moves MoneyBall DB from database design into **real data acquisition and implementation**.

The objective is to determine whether we can reliably source, automate, validate and store the historical data required to make the MoneyBall DB concept feasible.

### Version 1 — Proof of Feasibility

The current 7-table schema represents **Version 1 of an expandable database**.

It is deliberately limited to seven foundational tables so that we can test the feasibility of the project before significantly expanding the database.

The seven tables are:

1. `trading_days`
2. `daily_market_data`
3. `market_outcomes`
4. `asset_regimes`
5. `macro_conditions`
6. `scheduled_events`
7. `calendar_context`

These are **not intended to represent the final MoneyBall DB**.

Future phases may introduce many additional tables, datasets and research dimensions as new hypotheses and requirements emerge.

Phase 2 will also test the schema itself against real-world data. Therefore, the current table structures are not locked.

During source research and implementation:

- columns may be added,
- columns may be removed,
- definitions may change,
- sourced fields may become derived fields,
- and relationships may be adjusted.

The schema should evolve when real data demonstrates that a better structure is required.

### Phase 2 Approach

Each table will be reviewed individually.

For each table we will:

1. Review its fields and determine what must be **sourced** and what can be **derived**.
2. Research appropriate data sources.
3. Prefer **free, automated, reliable and historically comprehensive** sources where possible.
4. Test candidate sources before committing to them.
5. Build the required acquisition and transformation pipeline.
6. Validate the resulting data.
7. Store the data in PostgreSQL.
8. Confirm that the dataset can be updated and reproduced.

A single source may support multiple tables, while some tables may require multiple sources.

### Data Pipeline

The standard pipeline will be:

**Fetch → Normalize → Derive → Validate → Store**

Provider-specific formats should remain separate from the core MoneyBall DB schema.

Derived research fields should generally be calculated internally so that their definitions remain deterministic and reproducible.

### Research Integrity

Special attention must be given to **look-ahead bias**.

Historical data must represent information that was actually available at the point in time being studied, particularly for macroeconomic data, scheduled releases and other information that may later be revised.

### PostgreSQL Implementation

Phase 2 will establish and progressively populate the local PostgreSQL database.

The system should support:

- schema management through Alembic migrations,
- reproducible historical data acquisition,
- incremental updates,
- data validation,
- and complete rebuilds from a fresh clone.

The repository remains the **recipe** and the database remains a **rebuildable result**.

### Phase 2 Completion

Phase 2 is complete when we have demonstrated that the initial 7-table MoneyBall DB is feasible and can be reliably:

**Built → Populated → Validated → Updated → Rebuilt**

The result will be **Version 1 of the MoneyBall DB research database**, not the finished database.

Future phases can then expand the schema with additional tables and datasets as the research develops.