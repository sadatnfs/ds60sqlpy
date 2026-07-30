# Catalog dependency labels and setup profiles

The catalog's `dependency_group` is a learner-facing readiness label. It is not
always the name of a `pyproject.toml` extra. Do not blindly turn every catalog
value into `pip install -e ".[VALUE]"`.

| Catalog label | What the lesson needs | How to prepare |
|---|---|---|
| `core` | Python standard library and course tools | Run the normal setup script |
| `data` | NumPy, pandas, plotting, statistics, and scikit-learn | Run the normal setup script |
| `postgres` | The disposable PostgreSQL course database and `psql` | Follow the [PostgreSQL setup](../sql/postgres-60day/README.md) |
| `bridge` | psycopg, pooling, and Python/PostgreSQL integration | Run advanced setup, or install the `bridge` extra |
| `professional` | Packaging (`build`, `setuptools`, and `wheel`), Arrow/Parquet, DuckDB, and property-based tests | Run advanced setup, or install the `professional` extra |
| `quality` | pytest, Hypothesis-aware test tooling, type checking, and linting | Run normal setup plus the `professional` extra for Hypothesis |
| `sql-notebooks` | Jupyter SQL magics, SQLAlchemy, and the Psycopg 3 PostgreSQL driver | Run advanced setup, or install the `sql-notebooks` extra |
| `geo` | Geospatial Python packages | Run advanced setup, or install the `geo` extra |
| `ml` | Optional advanced machine-learning libraries | Run advanced setup, or install the `ml` extra |
| `production` | FastAPI, Dask, MLflow, and Prefect | Run advanced setup, or install the `production` extra |
| `deep-learning` | PyTorch and torchvision | Run advanced setup, or install the `deep-learning` extra |
| `nlp` | Transformers, datasets, evaluation, and spaCy | Run advanced setup, or install the `nlp` extra |
| `advanced` | Capstone readiness across several optional groups | Run the aggregate advanced setup; there is intentionally no `advanced` extra |

The setup scripts are the simplest route:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
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
.\.venv\Scripts\python.exe -m pip install -e ".[bridge]"
```

```bash
# Example on macOS or Linux
.venv/bin/python -m pip install -e ".[bridge]"
```

Replace `bridge` only with a real extra listed in `pyproject.toml`. First-run
data/model downloads are separate from package installation; consult the
lesson's catalog `network` value and companion guide before going offline.
