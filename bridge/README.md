# Python + PostgreSQL engineering bridge

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Python + PostgreSQL engineering** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work.


The main Python and SQL tracks teach each language well. This optional
eight-lesson bridge teaches the engineering habits needed to use them together
safely in an application, data pipeline, or command-line tool. Five named
professional modules then add PostgreSQL notebooks, migration observability,
local AI application engineering, a local analytics-engineering project and
an evidence-driven integrated capstone.

## Who this is for

Start after completing at least:

- Python Day 15 (the command-line interface project), and
- SQL Day 15 (the first reporting project).

The bridge assumes you can write functions, classes, tests, joins, aggregates,
and basic data-changing SQL. If either prerequisite feels shaky, review it
before continuing. Bridge Day 1 depends on both prerequisites; every later
bridge day depends on the previous bridge day.

## Start the classroom

```bash
./classroom --starter
```

Choose **Python + PostgreSQL engineering** and open the intended unit. The
classroom provides Python Core and the disposable PostgreSQL service. Most
bridge examples use deterministic in-memory fakes; real database steps are
explicitly identified. Never substitute SQLite for a PostgreSQL concurrency,
type or transaction experiment.

The dedicated interactive JupySQL notebook uses a separately prepared
[contributor notebook workflow](../docs/setup/jupyter-postgresql.md). Other
external project steps also state their own preparation. These are extensions
to study, not alternate product installers. Keep connection values private and
use only the local disposable course database.

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

The fifth named unit, [bridge-capstone-01](professional/companion-guides/bridge_capstone_01_evidence_review.md),
combines independent fixtures, correctness checks and an evidence review.

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

## Contributor validation

Prepare the environment in [CONTRIBUTING](../CONTRIBUTING.md), then run from
the repository root on Linux/macOS or Windows WSL 2:

```bash
uv run --no-sync python -m pytest bridge/tests bridge/professional/tests -q
uv run --no-sync python bridge/scripts/validate_bridge.py
uv run --no-sync python scripts/validate_notebooks.py
```

Structural checks and fake-session tests do not prove a live connection or
transaction observation. Record explicitly prepared integration results
separately. Browser pads and results stay in the Docker learning volume;
contributor file changes do not automatically update those pads.

## Safety rules

- Never run the course code against production or a shared database.
- Never log a full connection string, password, token, or record payload.
- Bind values with Psycopg `%s` placeholders. Do not build SQL with f-strings.
- Compose dynamic identifiers only with `psycopg.sql.Identifier`.
- Keep transactions short and make retry scope explicit.
- A checkpoint advances only after its durable write succeeds.
