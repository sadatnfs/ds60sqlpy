# Python + PostgreSQL engineering bridge

The main Python and SQL tracks teach each language well. This optional
eight-lesson bridge teaches the engineering habits needed to use them together
safely in an application, data pipeline, or command-line tool. Four named
professional modules then add PostgreSQL notebooks, migration observability,
local AI application engineering, and a local analytics-engineering project.

## Who this is for

Start after completing at least:

- Python Day 15 (the command-line interface project), and
- SQL Day 15 (the first reporting project).

The bridge assumes you can write functions, classes, tests, joins, aggregates,
and basic data-changing SQL. If either prerequisite feels shaky, review it
before continuing. Bridge Day 1 depends on both prerequisites; every later
bridge day depends on the previous bridge day.

## Environment

- Python 3.11 or 3.12
- PostgreSQL 16 or newer for optional live exercises
- the repository development/quality dependencies
- Psycopg 3 for live database exercises

The code and tests use small in-memory fakes by default, so the core track is
deterministic and runnable offline. A live PostgreSQL exercise is always marked
**optional live-DB step**. Never substitute SQLite: its parameter syntax,
transactions, types, and concurrency behavior differ from PostgreSQL.

Install the advanced course profile once while connected:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
```

```bash
bash scripts/setup.sh --advanced
```

Store the disposable course connection string in `DS60_DATABASE_URL`. Do not
commit it and do not paste it into source files.

```powershell
# Windows PowerShell
$env:DS60_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.\.venv\Scripts\python.exe bridge\lessons\day01_config_logging_cli.py
```

```bash
# macOS/Linux
export DS60_DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.venv/bin/python bridge/lessons/day01_config_logging_cli.py
```

Use only the disposable course database for live exercises. Setup and reset
instructions live in [the PostgreSQL track](../sql/postgres-60day/README.md).

## Learning path

| Day | Topic | Learner file | Guide |
|---:|---|---|---|
| 1 | Configuration, logging, and typed CLI boundaries | [lesson](lessons/day01_config_logging_cli.py) | [guide](companion-guides/day01_config_logging_cli.md) |
| 2 | Protocols, context managers, and decorators | [lesson](lessons/day02_protocols_context_decorators.py) | [guide](companion-guides/day02_protocols_context_decorators.md) |
| 3 | Safe parameterized Psycopg queries | [lesson](lessons/day03_safe_psycopg_queries.py) | [guide](companion-guides/day03_safe_psycopg_queries.md) |
| 4 | Transactions, idempotency, and retries | [lesson](lessons/day04_transactions_idempotency_retries.py) | [guide](companion-guides/day04_transactions_idempotency_retries.md) |
| 5 | Database tests, fixtures, and test doubles | [lesson](lessons/day05_db_testing_fixtures_doubles.py) | [guide](companion-guides/day05_db_testing_fixtures_doubles.md) |
| 6 | Bulk ETL and validation | [lesson](lessons/day06_bulk_etl_validation.py) | [guide](companion-guides/day06_bulk_etl_validation.md) |
| 7 | Async I/O and bounded concurrency | [lesson](lessons/day07_async_bounded_concurrency.py) | [guide](companion-guides/day07_async_bounded_concurrency.md) |
| 8 | Production capstone | [lesson](lessons/day08_production_capstone.py) | [guide](companion-guides/day08_production_capstone.md) |

### Professional bridge modules

| Stable ID | Topic | Learner artifact | Guide |
|---|---|---|---|
| `bridge-jupyter-01` | PostgreSQL in Jupyter with `%sql` and `%%sql` | [notebook](professional/notebooks/bridge_jupyter_01_postgresql_magics.ipynb) | [guide](professional/companion-guides/bridge_jupyter_01_postgresql_magics.md) |
| `bridge-ops-01` | Migration delivery and application observability | [lesson](professional/lessons/bridge_ops_01_migration_observability.py) | [guide](professional/companion-guides/bridge_ops_01_migration_observability.md) |
| `bridge-ai-01` | Local AI application engineering | [lesson](professional/lessons/bridge_ai_01_application_engineering.py) | [guide](professional/companion-guides/bridge_ai_01_application_engineering.md) |
| `bridge-analytics-01` | Local analytics engineering | [lesson](professional/lessons/bridge_analytics_01_local_project.py) | [guide](professional/companion-guides/bridge_analytics_01_local_project.md) |

The Jupyter module has its own
[Windows/macOS/Linux setup guide](../docs/setup/jupyter-postgresql.md). It uses
the same disposable `advanced_sql_training` database and reads the connection
string from `DS60_DATABASE_URL`; the notebook never stores a password.

## How to study

For each day:

1. Read the companion guide.
2. Run the learner file once. It reports the exercises without calling
   unfinished functions.
3. Implement the `TODO` sections and add tests of your own.
4. Run the bridge tests and compare behavior, not just text output.
5. Use progressive hints before opening `solutions/`.
6. Complete any live-DB step only against the disposable course database.

The reference solutions are deliberately small. They show one sound design, not
the only acceptable design.

## Validation

From the repository root:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m compileall -q bridge
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
.\.venv\Scripts\python.exe bridge\scripts\validate_bridge.py
```

```bash
# macOS/Linux
.venv/bin/python -m compileall -q bridge
.venv/bin/python -m pytest bridge/tests -q
.venv/bin/python bridge/scripts/validate_bridge.py
```

`compileall` creates disposable `__pycache__` directories. They are ignored by
Git and can be deleted at any time; they are not course content.

Validate the professional bridge tests and notebook structure too:

```powershell
.\.venv\Scripts\python.exe -m pytest bridge\professional\tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\validate_notebooks.py
```

```bash
.venv/bin/python -m pytest bridge/professional/tests -q -p no:cacheprovider
.venv/bin/python scripts/validate_notebooks.py
```

## Safety rules

- Never run the course code against production or a shared database.
- Never log a full connection string, password, token, or record payload.
- Bind values with Psycopg `%s` placeholders. Do not build SQL with f-strings.
- Compose dynamic identifiers only with `psycopg.sql.Identifier`.
- Keep transactions short and make retry scope explicit.
- A checkpoint advances only after its durable write succeeds.
