# Python foundations and professional practice

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Python and data science** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


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

Do not edit the solution while attempting a lesson. Copy the learner artifact
to `.learning/` if you want to preserve your work independently of repository
updates.

## Run a learner artifact

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_pro_02_concurrency_parallelism.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pro_02_concurrency_parallelism.py
```

The standard-library paths work without network access. The Arrow/DuckDB module
detects optional packages and demonstrates a CSV fallback when they are absent.
The packaging module builds with isolation disabled, so it never attempts to
resolve build requirements from the internet.

The advanced modules remain local as well. Hypothesis is used with an
in-memory, deterministic profile and no example database; statistics use a
tracked CSV; model delivery uses JSON manifests and hashes; the service lab
injects identity, clocks, probes, and work instead of opening a socket; and the
performance lab reports measurements without asserting a universal speedup.

## Run the focused tests

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest discover -s python\professional\tests -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s python/professional/tests -v
```

The new boundary and failure drills also have a focused test suite:

```text
python -m pytest tests/test_python_expansion_boundaries.py
```

Use the same course interpreter selected in setup for that command. Some
integration checks in the original professional tests are reported as skipped when their optional package is
not installed. A skip is not silent: its message identifies the missing local
bootstrap dependency.

## Safety and generated files

- No module contacts a public network service.
- Build distributions, installed packages, Parquet files, and partitions go
  into a temporary directory or an ignored learner directory.
- The HTTP lesson uses an injected scripted transport; authentication examples
  use placeholders and redact sensitive headers.
- Process-pool code always lives behind a `if __name__ == "__main__":` guard so
  it is safe with Windows' `spawn` process start method.
