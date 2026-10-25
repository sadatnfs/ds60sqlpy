# Dependencies and execution profiles

Three kinds of names appear in DS60. They answer different questions:

| Name | Meaning | Source of truth |
| --- | --- | --- |
| Legacy `dependency_group` | Packages or services a Python/SQL/bridge lesson needs | `curriculum/catalog.json` |
| Module `runtime_profile` | The fixed environment for one lesson variant | `courses/*/lessons.json` and the runtime registry |
| Python project extra | Optional packages for a prepared Python environment | `pyproject.toml` and `uv.lock` |

Do not turn a label into an installation command without checking its contract.
For example, `postgres` means a database/client capability, while `advanced` is
an aggregate readiness label. Neither is an installable Python extra.

## Learners use prepared Docker runtimes

Start with `./classroom`. A new project prepares all ordinary workers. Use
`./classroom --starter` for the app, PostgreSQL and Python Core, or select specific
additional profiles. The selection is remembered. See [runtime profiles](modules-runtime.md)
and the [launcher guide](one-command-classroom.md).

Python Core, TensorFlow, PyTorch and PySpark are different prepared environments.
Selecting Python does not imply every library is installed. Opening a chapter or
pressing Run never installs arbitrary dependencies. HTML/CSS and browser JavaScript/D3
use the isolated browser preview; PHP uses its CLI worker with SQLite. Optional
CUDA and cluster operations require their separate explicit preparation.

## Legacy readiness labels

| Label | Capability |
| --- | --- |
| `core` | Python standard library and course tools |
| `data` | NumPy, pandas, plotting, statistics and scikit-learn |
| `bridge` | Psycopg and Python/PostgreSQL integration |
| `professional` | Packaging, Arrow/Parquet, DuckDB and property-based testing |
| `quality` | Contributor tests, typing and linting |
| `sql-notebooks` | JupySQL, SQLAlchemy and a PostgreSQL driver |
| `postgres` | Disposable course PostgreSQL and `psql` |
| `ml`, `production`, `geo`, `deep-learning`, `nlp` | Corresponding optional packages and separately declared assets |
| `advanced` | Several optional capabilities, determined by the lesson |

Core packages do not make every framework, server application or model workflow
runnable in a single-file pad. Use the declared worker or external project.
[Docker package options](docker-profiles.md) explains app-image customization
when a legacy Python lesson needs an additional package group.

## Contributor environments

Follow [CONTRIBUTING.md](../CONTRIBUTING.md). The POSIX setup helper supports:

```sh
bash scripts/setup.sh --dependency-mode locked
bash scripts/setup.sh --advanced --dependency-mode locked
```

Locked mode requires an existing `uv` installation. Project mode resolves declared
requirements without reproducing the lock and is not evidence for the locked release.
Automatic mode reports the tool it selects. Existing environments are validated,
not silently replaced. Windows contributors run these commands in WSL 2.

`uv sync` synchronizes selected extras exactly. A later smaller selection can remove
previously installed packages. Keep the intended extras in your command. Source,
learner work, database data and caches are separate from installed packages.

The root project and individual workers have different reviewed locks. Compiler
versions, packages and source limits come from Dockerfiles and runtime adapters,
not the host's installed tools. Platform markers describe dependency selection;
a resolved lock does not prove execution on that platform.

Weights, tokenizer assets, spaCy pipelines, map tiles and external services need
the exact preparation declared by their lessons. Verify offline assets separately
from package import success.
