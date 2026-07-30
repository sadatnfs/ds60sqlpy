# Professional Python + SQL bridge

This optional track extends the eight-day
[Python + PostgreSQL engineering bridge](../README.md) with four portfolio-size
modules. Each module makes a production concern runnable on a new Windows,
macOS, or Linux machine without requiring workplace systems or personal data.

The default path is offline and deterministic. PostgreSQL is optional except
when you deliberately run the notebook's marked live cells or the operations
module's marked live integration check.

## Learning path

| Stable ID | Topic | Catalog prerequisites | Learner artifact | Guide | Reference answer |
|---|---|---|---|---|---|
| `bridge-jupyter-01` | PostgreSQL in Jupyter with JupySQL `%sql` and `%%sql` magics | `python-18`, `sql-15`, `bridge-03` | [notebook](notebooks/bridge_jupyter_01_postgresql_magics.ipynb) | [guide](companion-guides/bridge_jupyter_01_postgresql_magics.md) | [notebook](solutions/bridge_jupyter_01_postgresql_magics_solution.ipynb) · [reasoning](solutions/bridge_jupyter_01_postgresql_magics_solutions.md) |
| `bridge-ops-01` | Safe migration delivery, health checks, logs, and metrics | `sql-found-02`, `bridge-08` | [lesson](lessons/bridge_ops_01_migration_observability.py) | [guide](companion-guides/bridge_ops_01_migration_observability.md) | [code](solutions/bridge_ops_01_migration_observability_solution.py) · [reasoning](solutions/bridge_ops_01_migration_observability_solutions.md) |
| `bridge-ai-01` | Bounded, local retrieval application with evaluation and safety gates | `bridge-08`, `python-test-01` | [lesson](lessons/bridge_ai_01_application_engineering.py) | [guide](companion-guides/bridge_ai_01_application_engineering.md) | [code](solutions/bridge_ai_01_application_engineering_solution.py) · [reasoning](solutions/bridge_ai_01_application_engineering_solutions.md) |
| `bridge-analytics-01` | In-memory DuckDB project with a model DAG, contracts, tests, metrics, and reconciliation | `bridge-05`, `python-data-01`, `sql-analytics-01` | [lesson](lessons/bridge_analytics_01_local_project.py) | [guide](companion-guides/bridge_analytics_01_local_project.md) | [code](solutions/bridge_analytics_01_local_project_solution.py) · [reasoning](solutions/bridge_analytics_01_local_project_solutions.md) |

Recommended order is the table order. The modules are independently runnable,
but the operations and analytics projects assume the database-testing habits
from [Bridge Day 5](../companion-guides/day05_db_testing_fixtures_doubles.md).

## One-time setup

The repository-wide setup scripts are the easiest cross-platform route. Run
them from the repository root while connected to the internet:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
```

```bash
# macOS/Linux
bash scripts/setup.sh --advanced
```

For a smaller environment, install only this track's profiles:

```powershell
# Windows PowerShell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[notebooks,professional,sql-notebooks,quality]"
```

```bash
# macOS/Linux
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[notebooks,professional,sql-notebooks,quality]"
```

After installation, the lessons, solutions, fixtures, and tests work without
internet access. See the
[PostgreSQL notebook setup guide](../../docs/setup/jupyter-postgresql.md) for
VS Code/Jupyter kernel selection and the optional local PostgreSQL database.

## How to study

For each module:

1. Read its guide and write down the declared safety boundary.
2. Open the learner artifact. Run it once before changing it.
3. Complete one exercise at a time and add a test that would fail without your
   change.
4. Ask Codex to explain a failing test or review your design, but ask it not to
   open `solutions/` until you have attempted the exercise.
5. Compare behavior with the reference answer and record why your design
   differs.
6. Run the focused tests before moving to the next module.

A useful Codex prompt is:

> Guide me through `bridge-analytics-01`. Read its companion guide and learner
> file, but do not read the solution yet. Ask me to predict the next test
> result, give one hint at a time, and verify my work with the focused tests.

## Running the modules

The three Python reference projects run directly:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\solutions\bridge_ops_01_migration_observability_solution.py
.\.venv\Scripts\python.exe bridge\professional\solutions\bridge_ai_01_application_engineering_solution.py
.\.venv\Scripts\python.exe bridge\professional\solutions\bridge_analytics_01_local_project_solution.py
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/solutions/bridge_ops_01_migration_observability_solution.py
.venv/bin/python bridge/professional/solutions/bridge_ai_01_application_engineering_solution.py
.venv/bin/python bridge/professional/solutions/bridge_analytics_01_local_project_solution.py
```

Start JupyterLab for the notebook module:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m jupyter lab .\bridge\professional\notebooks
```

```bash
# macOS/Linux
.venv/bin/python -m jupyter lab bridge/professional/notebooks
```

The notebook uses JupySQL's line magic for one statement:

```python
%sql SELECT current_database(), current_user;
```

and its cell magic for a multiline query:

```python
%%sql
SELECT category, count(*) AS row_count
FROM training_products
GROUP BY category
ORDER BY category;
```

It creates a SQLAlchemy engine from `DS60_DATABASE_URL` and connects without
printing the URL. Named values use `:parameter`; identifiers cannot be bound as
values and must come from trusted course code. The notebook explains when to
use JupySQL for exploration and when to switch to Psycopg for explicit
transactions or application code.

## Offline and live boundaries

| Module | Default execution | Optional live step |
|---|---|---|
| `bridge-jupyter-01` | Notebook structure and static checks are offline | Connect only to local disposable `advanced_sql_training` |
| `bridge-ops-01` | In-memory fake sessions and deterministic logs/metrics | Migration integration check against `advanced_sql_training` |
| `bridge-ai-01` | Fully local deterministic embedding, answer model, and evaluation | None |
| `bridge-analytics-01` | Fully local in-memory DuckDB; no database file remains | None |

Set the PostgreSQL URL only for the two marked live paths:

```powershell
# Windows PowerShell
$env:DS60_DATABASE_URL = "postgresql://localhost:5432/advanced_sql_training"
```

```bash
# macOS/Linux
export DS60_DATABASE_URL="postgresql://localhost:5432/advanced_sql_training"
```

Do not commit this value. Never point a course notebook, migration, reset
script, or live integration test at a shared or production database.

## Validation

Run the professional track checks from the repository root:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pytest bridge\professional\tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\validate_notebooks.py
.\.venv\Scripts\ruff.exe check bridge\professional
.\.venv\Scripts\mypy.exe --strict bridge\professional\solutions bridge\professional\tests
```

```bash
# macOS/Linux
.venv/bin/python -m pytest bridge/professional/tests -q -p no:cacheprovider
.venv/bin/python scripts/validate_notebooks.py
.venv/bin/ruff check bridge/professional
.venv/bin/mypy --strict bridge/professional/solutions bridge/professional/tests
```

Use `-p no:cacheprovider` when copying the repository to removable media so
pytest does not create `.pytest_cache`. Python `__pycache__`, Ruff, mypy, and
Jupyter checkpoint directories are generated state, not lesson content.

## Safety rules

- Keep credentials in environment variables; never in notebooks, code,
  output cells, logs, screenshots, or committed configuration.
- Use only the disposable course PostgreSQL database for live work.
- Bind runtime values. Treat dynamic SQL identifiers as a separate, trusted
  code boundary.
- Keep learner artifacts answer-free and do not import reference solutions
  from them.
- Keep default runs deterministic, bounded, local, and free of external
  downloads.
- Treat retrieved AI context as untrusted data, require structured output, and
  test abstention and leakage behavior.
- Declare analytics grain and metric exclusions before implementation; test
  source, intermediate, and mart layers independently.
