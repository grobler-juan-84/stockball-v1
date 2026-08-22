# MoneyBall DB

MoneyBall DB is a reproducible stock-market **research database and experimentation system**.

It is not a trading app. The goal is a trustworthy historical environment where market hypotheses can be tested honestly.

**The repository is the recipe. The database is the result.**

A clean clone should eventually rebuild the same research dataset from source data and project version — without copying a populated PostgreSQL database between machines.

See:

- [docs/project_manifesto.md](docs/project_manifesto.md) — project philosophy
- [docs/tech_stack.md](docs/tech_stack.md) — technical decisions

---

## Requirements

- Python **3.11+**
- Local **PostgreSQL**

---

## Local setup

1. Clone the repository.

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

3. Install the package (including test tools):

```bash
pip install -e ".[dev]"
```

4. Install and start PostgreSQL locally, then create an empty database:

```sql
CREATE DATABASE moneyball;
```

5. Copy the environment template and edit credentials:

```bash
cp .env.example .env
```

Set `DATABASE_URL` to your local PostgreSQL connection string (SQLAlchemy + psycopg v3 form).

6. Apply migrations (schema is empty for now; this verifies Alembic wiring):

```bash
alembic upgrade head
```

7. Run tests:

```bash
pytest
```

---

## Pipeline commands (stubs)

These entry points exist; data fetching and schema population are not implemented yet.

| Command | Purpose |
| ------- | ------- |
| `python scripts/build_database.py` | Full rebuild from source data |
| `python scripts/update_database.py` | Incremental update |
| `python scripts/validate_database.py` | Integrity / quality checks |
| `python scripts/reset_database.py` | Destructive reset (intentionally disabled) |

---

## Stack (initial)

Python · PostgreSQL · SQLAlchemy · Alembic · pandas · NumPy · python-dotenv · pytest
