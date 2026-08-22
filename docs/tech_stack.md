# MoneyBall DB — Initial Tech Stack

## 1. Architecture Principle

MoneyBall DB follows a **local-first, cloud-ready** architecture.

> **Local-first, cloud-ready.** The research database runs on local PostgreSQL during the sandbox phase. Data acquisition and schema management must be reproducible and environment-independent so the finalized database can later migrate to hosted PostgreSQL/Supabase without redesigning the data model.

Local PostgreSQL is our current **environment**.

PostgreSQL is our long-term **database architecture**.

Supabase is a potential future **hosting and application platform**, not a dependency of the research system.

This distinction is important.

The research pipeline must not depend on Supabase-specific functionality during the sandbox phase. Moving the finalized database from local PostgreSQL to hosted PostgreSQL/Supabase should primarily be a deployment change rather than a database redesign.

---

## 2. Initial Technical Philosophy

The initial stack is optimized for:

* Reproducibility across multiple computers
* Local-first development
* Future cloud portability
* Automated data acquisition
* Incremental data updates
* Reliable historical data storage
* Version-controlled schema management
* Deterministic derived data
* Simple research workflows
* Minimal infrastructure

The repository should contain everything required to reconstruct the research environment.

The populated database itself does not need to be synchronized between development computers.

---

# Core Stack

## 3. Python

**Purpose:** Primary programming language for the MoneyBall DB research infrastructure.

Python will power:

* Data-provider requests
* Data acquisition
* Data cleaning
* Data normalization
* Derived field calculations
* Database population
* Incremental updates
* Database rebuilds
* Data validation
* Research scripts
* Future experimentation

Python is the primary language of MoneyBall DB.

---

## 4. PostgreSQL

**Purpose:** Primary research database.

During the sandbox phase, PostgreSQL runs locally on each development computer.

It stores the structured historical dataset used by MoneyBall DB.

The database itself is **not synchronized between computers**.

Instead, each computer should be capable of reconstructing its database using:

* the Git repository
* database migrations
* configuration
* original data providers
* deterministic transformation logic

This allows Computer A and Computer B to independently construct equivalent research environments.

### Why PostgreSQL?

Using PostgreSQL locally means our research environment already uses the same fundamental database technology that can later run in a hosted environment.

This minimizes migration risk.

The long-term path is conceptually:

**Local PostgreSQL**

↓

**Finalized research database**

↓

**Hosted PostgreSQL / Supabase**

The data model should not require redesign simply because the database moves to the cloud.

---

## 5. SQL

**Purpose:** Schema definition, constraints, indexes, migrations, data inspection, and research queries.

SQL will be used directly where appropriate.

We should not hide the database behind unnecessary abstraction.

MoneyBall DB is fundamentally a data and research project, so understanding and controlling the underlying database structure is valuable.

---

# Python Database Layer

## 6. SQLAlchemy

**Purpose:** Python ↔ PostgreSQL communication.

SQLAlchemy provides the database layer used by Python pipelines.

It will support:

* database connections
* transactions
* inserts
* updates
* upserts
* queries
* schema metadata

Explicit SQL can still be used whenever it is clearer or more appropriate.

We should avoid building unnecessary repository/service abstractions designed for web applications.

---

## 7. Alembic

**Purpose:** Version-controlled database schema migrations.

The MoneyBall DB schema will evolve substantially as research expands.

Alembic allows schema changes to live alongside the source code.

This means a clean environment can reconstruct the correct database structure from repository history.

The intended workflow is:

**Git Clone**

↓

**Configure Environment**

↓

**Create PostgreSQL Database**

↓

**Run Alembic Migrations**

↓

**Correct Schema Exists**

This is also an important part of the **cloud-ready** architecture.

The same migration history should eventually be capable of constructing the database schema against a hosted PostgreSQL environment.

Schema creation must therefore avoid unnecessary machine-specific assumptions.

---

# Data Processing

## 8. pandas

**Purpose:** Tabular data manipulation and transformation.

Used for:

* Cleaning fetched datasets
* Normalizing provider data
* Aligning trading dates
* Joining datasets
* Calculating derived fields
* Preparing database inserts
* Research analysis
* Data validation

---

## 9. NumPy

**Purpose:** Numerical operations supporting pandas and future statistical research.

NumPy will be used where efficient numerical calculations are required.

---

# Configuration

## 10. Environment Variables

Machine-specific configuration and secrets must remain outside the repository.

A local:

`.env`

file can contain values such as:

* Database connection strings
* API keys
* Provider credentials
* Environment-specific configuration

Secrets must **never be committed to Git**.

The repository should contain:

`.env.example`

showing which configuration values are required.

### Environment Independence

Application and pipeline code must not assume that PostgreSQL is running at a particular hardcoded location.

For example:

`DATABASE_URL`

determines which PostgreSQL environment the project connects to.

During development this may point to:

**Local PostgreSQL**

Later it may point to:

**Hosted PostgreSQL / Supabase**

The pipeline should not need to be rewritten simply because the database location changes.

---

# Data Architecture

## 11. Raw Data

Where practical, provider responses should first be preserved as raw data before transformation.

Conceptually:

**Provider → Raw → Clean → Derive → Validate → PostgreSQL**

Raw data provides traceability and makes debugging/reprocessing easier.

Large raw datasets should normally remain outside Git.

---

## 12. Processed Data

Processed data represents cleaned or normalized intermediate datasets produced from raw provider data.

Processed files are working artifacts.

They are not the canonical definition of the research system.

The canonical logic lives in source code.

---

## 13. PostgreSQL Research Database

PostgreSQL stores the structured research dataset.

The database contains both observed and derived information, while the source code defines how derived information is calculated.

The database is therefore a **rebuildable artifact**.

The repository remains the recipe used to produce it.

---

# Data Provider Architecture

## 14. Multiple Data Providers

MoneyBall DB should not be architecturally dependent on a single financial-data provider.

Different tables may require different authoritative sources.

Potential categories include:

* Market prices
* Macroeconomic data
* Interest rates
* Scheduled economic releases
* Corporate events
* Calendar information
* Political/event data
* Sentiment data
* Future unconventional datasets

Each provider should have its own acquisition/adapter layer.

Provider-specific formats should be normalized before entering the core database.

The architecture should preserve the separation:

**FETCH**

↓

**NORMALIZE**

↓

**DERIVE**

↓

**VALIDATE**

↓

**STORE**

This means replacing one provider should not require redesigning the MoneyBall DB schema.

---

# Reproducibility

## 15. Git + GitHub

**Purpose:** Version control and the canonical definition of the project.

Git tracks:

* Source code
* Database migrations
* Fetch scripts
* Cleaning logic
* Transformation logic
* Derived-field logic
* Validation rules
* Configuration definitions
* Documentation
* Experiments

Git does **not** need to contain the populated PostgreSQL database.

The repository should contain everything required to recreate it.

---

## 16. Reproducible Data Cutoffs

Two computers running the same project version against the same defined data cutoff should produce equivalent research datasets.

This means data fetching must eventually support explicit boundaries rather than implicitly depending only on "whatever data exists today."

Where practical, the pipeline should know:

* requested start date
* requested end date
* latest stored date
* provider source
* transformation version

This becomes increasingly important as the research environment matures.

---

# Database Operations

## 17. Build

Creates the research database from the available source data.

Conceptually:

`python scripts/build_database.py`

The build process should:

**Fetch → Clean → Derive → Validate → Load**

---

## 18. Update

Updates an existing research database.

Conceptually:

`python scripts/update_database.py`

The update process should inspect existing data and retrieve only missing or newly available information wherever possible.

For example:

Database contains data through:

`2026-08-20`

Provider contains data through:

`2026-08-22`

The updater should fetch and process the missing period rather than downloading the complete historical dataset again.

---

## 19. Reset / Rebuild

Allows the research database to be deliberately reconstructed.

Conceptually:

`python scripts/reset_database.py`

This becomes useful when:

* major schema changes occur
* new foundational tables are introduced
* transformation logic changes substantially
* database integrity needs to be verified
* a completely clean research environment is required

Destructive operations must be explicit and protected against accidental execution.

---

## 20. Validate

Runs database and data-quality checks.

Conceptually:

`python scripts/validate_database.py`

Validation may eventually check:

* expected tables exist
* primary keys are unique
* required values are present
* date ranges are sensible
* foreign-key relationships are valid
* market-data rules are satisfied
* derived values can be reproduced
* tables share expected trading dates
* data freshness is known

Validation is a first-class part of the pipeline rather than an afterthought.

---

# Initial Reproduction Workflow

## 21. Fresh Computer

The intended workflow is:

**Git Clone**

↓

**Install Python Dependencies**

↓

**Install / Start PostgreSQL**

↓

**Configure `.env`**

↓

**Create Database**

↓

**Run Alembic Migrations**

↓

**Fetch Source Data**

↓

**Clean + Normalize**

↓

**Calculate Derived Fields**

↓

**Validate**

↓

**Populate PostgreSQL**

↓

**MoneyBall DB Ready**

No manually copied database should be required.

---

## 22. Existing Computer

When the database already exists:

**Git Pull**

↓

**Install Any New Dependencies**

↓

**Run New Migrations**

↓

**Check Existing Data**

↓

**Fetch Missing Data**

↓

**Process + Validate**

↓

**Upsert**

↓

**MoneyBall DB Updated**

---

# Schema Design

## 23. dbdiagram.io

dbdiagram.io is used during the design phase to visually design and discuss the MoneyBall DB schema.

It is a planning and documentation tool.

The dbdiagram representation is **not** the authoritative production schema.

Once implemented, the authoritative schema is represented by the PostgreSQL/Alembic migration history stored in Git.

---

# Future Hosting

## 24. Supabase / Hosted PostgreSQL

Supabase is **not required during the sandbox phase**.

However, MoneyBall DB should remain compatible with eventual migration to Supabase or another hosted PostgreSQL environment.

A future hosted architecture may allow:

* One centralized MoneyBall database
* Multiple users accessing the same underlying market dataset
* User-specific profiles and settings stored separately
* Application APIs
* Authentication
* Remote access
* Scheduled cloud updates

Importantly, 100 future users should **not** independently fetch and reconstruct the same market dataset.

The eventual architecture can maintain one shared canonical research database while user-specific information lives in separate application tables.

That is a future concern.

For now, we build and prove the research database locally.

---

# Not Required Yet

## 25. Deliberately Deferred Technologies

The following are deliberately postponed:

* React
* Web frontend
* REST API
* GraphQL
* Authentication
* Supabase integration
* Cloud hosting
* Docker
* Production deployment infrastructure
* Background workers
* Complex orchestration systems
* User profiles
* Multi-user infrastructure

These should only be introduced when the project actually requires them.

We should not solve production problems before proving the research system.

---

# Initial Stack Summary

| Layer                       | Technology                     |
| --------------------------- | ------------------------------ |
| Primary language            | Python                         |
| Database                    | PostgreSQL                     |
| Database access             | SQLAlchemy                     |
| Schema migrations           | Alembic                        |
| Data processing             | pandas                         |
| Numerical processing        | NumPy                          |
| PostgreSQL driver           | psycopg                        |
| Configuration               | `.env` / environment variables |
| Testing                     | pytest                         |
| Schema design               | dbdiagram.io                   |
| Version control             | Git                            |
| Repository                  | GitHub                         |
| Initial environment         | Local                          |
| Future database environment | Hosted PostgreSQL / Supabase   |

---

# Architectural Rules

1. **Local-first, cloud-ready.**
2. **The repository is the recipe. The database is the result.**
3. **A fresh clone must eventually be capable of reconstructing the research environment.**
4. **Never hardcode infrastructure that prevents moving between PostgreSQL environments.**
5. **Fetching, cleaning, deriving, validating, and storing data remain separate concerns.**
6. **Provider-specific formats must not dictate the core database schema.**
7. **Schema changes are version-controlled through migrations.**
8. **Existing databases should update incrementally rather than unnecessarily refetching everything.**
9. **Full rebuilds must remain possible.**
10. **Do not introduce production infrastructure until the research system requires it.**

---

# Guiding Principle

**The repository is the recipe. The database is the result.**

Build locally.

Make it reproducible.

Keep it portable.

Prove the research first.

Then move it to the cloud when there is a reason to.
