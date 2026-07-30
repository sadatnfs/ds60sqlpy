# Python professional practice

This optional track closes engineering gaps that sit between the numbered
Python lessons and production work. The ten modules are offline after the
repository setup: they use local files, deterministic workloads, injected
transports, and temporary directories.

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

Some integration checks are reported as skipped when their optional package is
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
