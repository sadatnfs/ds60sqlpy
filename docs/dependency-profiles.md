# Catalog dependency labels and setup profiles

The catalog's `dependency_group` is a learner-facing readiness label. It is not
always the name of a `pyproject.toml` extra. Do not blindly turn every catalog
value into `pip install -e ".[VALUE]"`.

| Catalog label | What the lesson needs | How to prepare |
|---|---|---|
| `core` | Python standard library and course tools | Run the normal setup script |
| `data` | NumPy, pandas, plotting, statistics, and scikit-learn | Run the normal setup script |
| `postgres` | The disposable PostgreSQL course database and `psql` | Follow the [PostgreSQL setup](../sql/postgres-60day/README.md) |
| `bridge` | psycopg, pooling, and Python/PostgreSQL integration | Included in normal Core setup |
| `professional` | Packaging (`build`, `pip`, `setuptools`, and `wheel`), Arrow/Parquet, DuckDB, and property-based tests | Included in normal Core setup |
| `quality` | pytest, Hypothesis-aware test tooling, type checking, and linting | Included in Core, including the `professional` extra for Hypothesis |
| `sql-notebooks` | Jupyter SQL magics, pandas result conversion, SQLAlchemy, and the Psycopg 3 PostgreSQL driver | Included in normal Core setup |
| `geo` | Geospatial Python packages | Run advanced setup, or install the `geo` extra |
| `ml` | Optional advanced machine-learning libraries | Run advanced setup, or install the `ml` extra |
| `production` | FastAPI, Dask, MLflow, and Prefect | Run advanced setup, or install the `production` extra |
| `deep-learning` | PyTorch and torchvision | Run advanced setup, or install the `deep-learning` extra |
| `nlp` | Transformers, datasets, evaluation, and spaCy | Run advanced setup, or install the `nlp` extra |
| `advanced` | Capstone readiness across several optional groups | Run the aggregate advanced setup; there is intentionally no `advanced` extra |

The `deep-learning` extra uses platform markers rather than assuming one wheel
works everywhere. Windows and Linux use the current compatible
PyTorch/TorchVision pair. Intel macOS uses the final published Intel-wheel
pair, while Apple Silicon uses a pair that remains installable on macOS 13.
These versions still support the tensor, training-loop, and transfer-learning
APIs used by the course.

The setup scripts are the simplest route:

```powershell
# Windows PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1 -Profile Advanced

$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
```

```bash
# macOS or Linux
bash scripts/setup.sh --advanced
```

Maintainers or learners conserving disk space may install one exact extra
after the normal setup has installed the shared notebook/data/quality
baseline:

```powershell
# Example on Windows
& $CoursePython -m pip install -e ".[bridge]"
```

```bash
# Example on macOS or Linux
.venv/bin/python -m pip install -e ".[bridge]"
```

Replace `bridge` only with a real extra listed in `pyproject.toml`. First-run
data/model downloads are separate from package installation; consult the
lesson's catalog `network` value and companion guide before going offline.

## Installation modes and evidence

Windows bootstrap accepts `-DependencyMode Auto`, `Locked`, or `Project`.
macOS/Linux setup accepts `--dependency-mode auto`, `locked`, or `project`.
Auto uses an existing standalone `uv` installation; otherwise pip resolves
project declarations. Locked requires `uv` and verifies agreement between
`uv.lock` and `pyproject.toml`. Project does not reproduce exact locked versions.

`uv sync` performs exact synchronization. Running Core after Advanced in locked
mode removes packages outside the selected Core profile. Choose Advanced again
when you need all optional groups. Source files, notebooks, progress, and
datasets are separate from installed packages. See
[uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/).

Both setup paths validate and reuse the repository environment; they do not
replace a broken `.venv` automatically. The POSIX script expects
`.venv/bin/python`. Virtual environments depend on their base interpreter and
location: copy source and recreate `.venv` rather than copying an environment
to another machine. See [Python venv](https://docs.python.org/3.12/library/venv.html).

The supported course range remains Python 3.11-3.12. Binary packages also depend
on OS and CPU. A lock resolution for another platform proves dependency
selection, not native execution there. Advanced imports do not download or
verify model assets. Check the actual CI run before treating a configured
matrix job as passing evidence.
