# Professional Python + SQL bridge

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Python + PostgreSQL engineering** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work.


This optional track extends the eight-day
[Python + PostgreSQL engineering bridge](../README.md) with named portfolio-size
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

The integrated [evidence-driven capstone](companion-guides/bridge_capstone_01_evidence_review.md)
adds `bridge-capstone-01` after `bridge-08`, `sql-quality-01`, and
`python-pro-03`. It uses independent synthetic golden fixtures to reject a
misleadingly healthy summary, reconstruct a correct product, gate a fake
publication, and write a bounded incident review. Its default requires only
the Python standard library and performs no live publication or database work.
The exact current inventory and prerequisites come from
`python scripts/course.py catalog --track bridge`.

Recommended order is the table order. The modules are independently runnable,
but the operations and analytics projects assume the database-testing habits
from [Bridge Day 5](../companion-guides/day05_db_testing_fixtures_doubles.md).

## Prepare the selected workflow

Use `./classroom --starter` and choose **Python + PostgreSQL engineering** for
the normal browser route. Read the selected unit's capability notice before
running. Live database, notebook and external project steps are explicit;
opening a guide does not prepare a host notebook interpreter.

For the dedicated JupySQL unit, follow the
[optional notebook guide](../../docs/setup/jupyter-postgresql.md). For direct
project files and tests, follow [contributor setup](../../CONTRIBUTING.md) on
Linux/macOS or Windows WSL 2. Prepare required packages while connected before
claiming an offline run.

## How to study

For each module:

1. Read its guide and write down the declared safety boundary.
2. Open the learner artifact. Run it once before changing it.
3. Complete one exercise at a time and add a test that would fail without your
   change.
4. Ask an AI tutor to explain a failing test or review your design, but ask it not to
   open `solutions/` until you have attempted the exercise.
5. Compare behavior with the reference answer and record why your design
   differs.
6. Run the focused tests before moving to the next module.

A useful AI tutor prompt is:

> Guide me through `bridge-analytics-01`. Read its companion guide and learner
> file, but do not read the solution yet. Ask me to predict the next test
> result, give one hint at a time, and verify my work with the focused tests.

## Running the modules

In the classroom, work in a saved learner pad and inspect the matching run
record. The source and notes survive normal stop/resume in the same project.
Reference solutions remain separate until you choose comparison.

Prepared contributors can run a particular source directly, for example:

```bash
uv run --no-sync python bridge/professional/lessons/bridge_ai_01_application_engineering.py
```

The notebook's `%sql` and `%%sql` work only in its prepared IPython kernel.
It validates the local course target, uses a SQLAlchemy engine without printing
its URL, and distinguishes bound values from generated identifiers. Follow
its guide rather than pasting notebook magics into a Python script.

## Offline and live boundaries

| Module | Default execution | Optional live step |
|---|---|---|
| `bridge-jupyter-01` | Notebook structure and static checks are offline | Connect only to local disposable `advanced_sql_training` |
| `bridge-ops-01` | In-memory fake sessions and deterministic logs/metrics | Migration integration check against `advanced_sql_training` |
| `bridge-ai-01` | Fully local deterministic embedding, answer model, and evaluation | None |
| `bridge-analytics-01` | Fully local in-memory DuckDB; no database file remains | None |

For marked live paths, supply the private connection through the shell
that launches the tool, using the actual local port from `./classroom status`.
The [notebook setup guide](../../docs/setup/jupyter-postgresql.md) shows a hidden
prompt. Never commit a URL or point a reset or integration test at shared data.

## Contributor validation

After [contributor setup](../../CONTRIBUTING.md), run:

```bash
uv run --no-sync python -m pytest bridge/professional/tests -q
uv run --no-sync python scripts/validate_notebooks.py
```

A structural or fake-session check is separate from a real database observation.
Use the [validation guide](../../docs/validation.md) for lint, typing and broader
release checks. Generated caches and notebook checkpoints are not course content.

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
