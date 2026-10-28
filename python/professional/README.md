# Python foundations and professional practice

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Python and data science** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work.


These named modules provide a gentler route into the numbered Python lessons
and deeper practice beyond them. Foundation checkpoints appear at their
prerequisite milestones; professional modules can take several sessions each.
The stable IDs describe learning units, not a deadline or a promise that every
unit takes one day. Modules use local files, deterministic workloads, injected
transports, and temporary directories after connected setup.

## Beginner confidence checkpoints

The catalog inserts four checkpoints into the early numbered route:

- After Day 1, [read and trace a program](companion-guides/py_foundations_01_read_trace_state.md)
  using straight-line statements and handwritten predictions.
- After Day 3, [debug from evidence](companion-guides/py_foundations_02_debug_evidence.md)
  before loops make execution harder to track.
- After Day 8, [clean trustworthy records](companion-guides/py_foundations_03_clean_records.md)
  with explicit zero/missing/invalid and duplicate policies.
- After Day 10, [finish a small auditable investigation](companion-guides/py_foundations_04_first_investigation.md)
  with a local CSV, independent checks, JSON readback, and a bounded conclusion.

The first two checkpoints do not presume loops or user-defined functions. The
later pair combines concepts already taught rather than requiring a table
library. Each has eight prediction, construction, diagnosis, and transfer
exercises with separate solution reasoning. Use the catalog to check direct
prerequisites and current ordering:

```text
python scripts/course.py catalog --track python
```

## Recommended route

| Stable ID | Module | Catalog prerequisites | Optional packages |
| --- | --- | --- | --- |
| `python-pro-01` | [Package engineering and local releases](companion-guides/py_pro_01_package_engineering.md) | `python-15` | `build`, `setuptools`, `wheel` |
| `python-pro-02` | [Concurrency and parallelism](companion-guides/py_pro_02_concurrency_parallelism.md) | `python-15` | None |
| `python-data-01` | [Arrow, Parquet, and DuckDB](companion-guides/py_data_01_arrow_duckdb.md) | `python-23` | `pandas`, `pyarrow`, `duckdb` |
| `python-svc-01` | [Reliable HTTP clients](companion-guides/py_svc_01_reliable_http_clients.md) | `python-15` | None |
| `python-test-01` | [Test architecture and generative testing](companion-guides/py_test_01_architecture_generative.md) | `python-10` | `hypothesis` |
| `python-lang-01` | [Advanced typing and the data model](companion-guides/py_lang_01_typing_data_model.md) | `python-12` | None |
| `python-stats-01` | [Resampling and experiments](companion-guides/py_stats_01_resampling_experiments.md) | `python-32` | None |
| `python-ml-01` | [Reproducible model delivery](companion-guides/py_ml_01_reproducible_delivery.md) | `python-45` | None |
| `python-svc-02` | [Service hardening and observability](companion-guides/py_svc_02_hardening_observability.md) | `python-55`, `bridge-08`, `python-svc-01`, `python-ml-01` | None |
| `python-perf-01` | [Measurement-first performance engineering](companion-guides/py_perf_01_measurement_optimization.md) | `python-23`, `python-pro-02` | Optional `numpy` |

## Deeper data and reliability labs

Three additional standard-library labs close gaps that do not require deep
learning packages or live services:

- [Exact values, Unicode identity, and calendar boundaries](companion-guides/py_data_02_exact_values_time_text.md)
  distinguishes approximate floats from exact cents, preserves normalization
  collisions, and assigns UTC window endpoints explicitly.
- [Leakage-resistant group/time evaluation](companion-guides/py_ml_02_group_time_evaluation.md)
  audits entity membership, feature and label availability, fold coverage, and
  train-only fitting before comparing model scores. Day 50 is optional.
- [Restartable local file pipelines](companion-guides/py_pro_03_restartable_file_pipeline.md)
  pins input bytes, publishes progress and results in one checkpoint, injects
  a pre-replacement failure, and tests resume without claiming universal
  power-loss or multi-writer guarantees.

Each module has four deliberately separate artifacts:

- `lessons/<stem>.py` is the learner workspace. It runs, but its exercises
  contain `TODO` markers rather than complete answers.
- `companion-guides/<stem>.md` explains the ideas and the exercise sequence.
- `solutions/<stem>_solution.py` is an executable reference implementation.
- `solutions/<stem>_solutions.md` explains the reasoning, alternatives, and
  edge cases.

Work in the classroom's saved learner pad while attempting a lesson.
Tracked starter and solution files remain separate from your Docker-volume work.

## Language mechanics and lifecycle

The additional standard-library path teaches mechanisms that affect real
program behavior:

- [Scope, closures and decorators](companion-guides/py_lang_02.md) traces lexical lookup, binding time, captured state and callable metadata.
- [Iterators, generators and resource lifetime](companion-guides/py_lang_03.md) distinguishes a consumable stream from a reusable container and makes cleanup ownership explicit.
- [Structured asyncio and cancellation](companion-guides/py_lang_04.md) teaches bounded concurrent work, deadlines, grouped failures and context restoration.

Follow each unit's direct catalog prerequisites. These are separate learning
units with saved pads and explained references, using the existing Core runtime.

## Deeper arrays, tables and algorithms

The catalog includes `python-numpy-01` through `python-numpy-08`,
`python-pandas-01` through `python-pandas-07`, and `python-algo-01` through
`python-algo-07`. These expand shapes and broadcasting, numerical behavior,
table grain and joins, data cleaning, collection design and algorithmic cost.
Use their actual prerequisite chains rather than treating the numbered route
as a mandatory completion barrier.

## Run and preserve an attempt

Run `./classroom --starter` from the repository root, choose Python and select
the unit by stable ID. Read its capability notice, edit the learner pad and
inspect saved run output. Standard-library examples are local and bounded.
Modules using packages such as Arrow, DuckDB or Hypothesis declare them; a
fallback example does not establish the behavior of an unavailable package.

The packaging fixture disables build isolation to avoid unplanned downloads.
Other projects use injected transports, local fixtures and temporary directories
where their guides specify them. Read each lesson's exact limitations before
claiming a network service, production release or performance improvement.

## Contributor verification

For direct scripts and focused tests, first prepare the environment in
[CONTRIBUTING](../../CONTRIBUTING.md). On Linux/macOS or Windows WSL 2:

```bash
uv run --no-sync python python/professional/lessons/py_pro_02_concurrency_parallelism.py
uv run --no-sync python -m pytest python/professional/tests tests/test_python_expansion_boundaries.py -q
```

These commands use host contributor files, not browser pad state. Missing
optional packages must be reported as skips or preparation gaps, not successful
runtime coverage. The [validation guide](../../docs/validation.md) describes
parallel checks and their evidence scope.

## Safety and generated files

- No module contacts a public network service.
- Build distributions, installed packages, Parquet files, and partitions go
  into a temporary directory or an ignored learner directory.
- The HTTP lesson uses an injected scripted transport; authentication examples
  use placeholders and redact sensitive headers.
- Process-pool code always lives behind a `if __name__ == "__main__":` guard so
  it is safe with Windows' `spawn` process start method.

The later deepening units include explicit dtype/promotion and overflow policies,
owned random streams and checkpoints, weighted least squares/SVD, and window/FFT
mechanics. Table work adds compound identity and lossless reshape, actual DST
and calendar boundaries, and exact typed CSV/Parquet/domain checks. Algorithms
add trees/tries, disjoint sets/minimum spanning forests, and one-pass summaries,
medians and reservoir sampling. The catalog owns exact prerequisites and paths.
