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

## Data and scientific additions

`data-engineering`, `data-platforms-python`, `dbt-duckdb`, `stan-cpu` and `julia` are ordinary launcher
profiles, not root Python extras. Their images and reviewed locks own their
dependencies. Polars and the canonical dbt/ML engineering programs run through
`data-engineering`, including pinned skops for the current MLflow scikit-learn model format; beginner dbt SQL-model variants use `dbt-duckdb`. Stan uses
native `main.stan` compilation; Julia uses `main.jl` and a prepared project/depot.
PyArrow/DataFusion/PyIceberg use `data-platforms-python` with separate native AMD64 and ARM64 hash locks. Ballista needs its separately matched environment and newer glibc; it is not installed in that worker. PyMC/ArviZ remain in `bayesian-cpu`. Do not merge those package environments just
because several courses contain Python source.

New projects include these ordinary profiles in the default selection. Existing
projects retain their saved selection; use `--all` or explicit profiles to add
new runtimes deliberately. `resume` never prepares them. See the
[scientist roadmap](scientist-roadmap.md) and [source contracts](modules-runtime.md)
for lesson placement, single-source boundaries and separate project workflows.


## Python web and independent scientific projects

`python-web` is an ordinary runtime profile, distinct from Python Core and root
project extras. It provides separately pinned Flask, FastAPI, Django, Django REST
Framework, SQLAlchemy, HTTP clients and related packages for finite `main.py`
programs. Native AMD64/ARM64 locks live under `docker/workers/`. In-process test
clients exercise application behavior without opening a persistent service.
The [owned web lab](../courses/python-web/projects/web-lab/README.md) adds actual
HTTP servers, PostgreSQL, jobs, streaming and browser/session state. Prepare its
small project image explicitly, and preserve its private workshop state through
stop/resume or replacement. A finite pad result does not qualify that lifecycle.

The [independent Spark likelihood package](../packages/spark-likelihood/README.md)
is distribution `ds60-spark-likelihood`, imported as `ds60_spark_likelihood`.
Its pure core has no mandatory third-party or classroom dependency. Spark,
CPU Torch, SciPy and distributed-training integrations are explicit extras.
The [Spark/Torch workshop](../courses/advanced-spark-modeling/projects/spark-torch/README.md)
prepares their compatible versions together, builds the pure wheel and installs
it before explicitly preparing the pinned Spark launcher. Fitting never downloads
packages or changes the user's Spark installation. The ordinary Spark and Torch
pads remain separate environments.

The package supports bounded row-additive and complete-independent-unit
likelihoods, declared predictions, DataFrame mapping and ML/Pipeline persistence.
It does not provide arbitrary cross-group covariance, a generic Laplace solver
or an unbounded neural-network driver optimizer. R is not required. The
[optional Spark/TMB reference](../courses/advanced-spark-modeling/projects/spark-tmb/README.md)
has its own R/TMB/C++ preparation, compiled-artifact identities and process boundary.
It consumes only the pure core contracts and is qualified separately.

Full ordinary publication currently covers 26 catalog images, App plus 25 workers.
Optional GPU profiles and scientific project images are separate contracts.
The full native scientific gate builds its project environments from that run's
qualified ordinary bases; it does not add them to a learner's default workers or
publish their local project tags automatically. See [validation](validation.md)
for the separate source, wheel, runtime, browser and hosted-release evidence.
