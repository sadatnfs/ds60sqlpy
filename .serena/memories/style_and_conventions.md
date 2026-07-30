# Style and conventions

## Shared course content

- Stable lesson names use zero-padded IDs such as `day01_topic` and catalog IDs
  such as `python-01`, `sql-01`, or `bridge-01`. Named extensions keep
  descriptive IDs such as `python-data-01`, `sql-found-01`, and
  `bridge-jupyter-01`; never renumber Days 1-60 to insert them.
- Define vocabulary before use. Pair motivation and small runnable examples with explicit level/prerequisites, learning objectives, graduated exercises, self-checks, next steps, and separate solutions.
- Keep the learner solving: do not place full answers in learner artifacts or reveal official solutions before an honest attempt.
- Use deterministic, laptop-safe examples unless randomness, scale, network, GPU, or external services are the explicit topic.
- Use UTF-8, LF line endings, repository-relative paths, and separately labeled PowerShell/POSIX blocks when syntax differs.
- Route learner-generated files to ignored `artifacts/dayXX/` locations. Treat `.learning/`, `artifacts/`, and `mlruns/` as potentially valuable local state even though Git ignores them.

## Python and notebooks

- Supported Python is 3.11-3.12; 3.12 is recommended.
- Prefer modern built-in generics, explicit return types for shared tooling, concise public docstrings, `pathlib`, context managers, and direct dependency declarations.
- Keep notebooks nbformat 4.5 with kernel name `ds60sqlpy`, display name `Python (ds60sqlpy)`, stable IDs, course/cell tags, no saved outputs, no machine-specific paths, and no hidden state.
- Network, slow, GPU, geospatial, Docker, and manual cells must be tagged. CPU and offline-after-bootstrap are defaults.
- Seaborn first-run sample-data downloads are accepted when disclosed and cached. Pretrained/model/map downloads must be optional and explicit.

## PostgreSQL and bridge

- Target PostgreSQL 16+; canonical CI uses PostgreSQL 17.
- Use `BEGIN`, `SET search_path TO training, public`, deterministic ordering where claimed, and `ROLLBACK` for ordinary lessons.
- Days 52-54 are the documented exception: Day 52 creates/commits the disposable `dwh` schema and Days 53-54 consume it in order.
- Use current schema names/columns, qualify ambiguous columns, explain NULL/time-zone/money assumptions, and never treat parse success as semantic proof.
- Run every SQL file with `psql -X -v ON_ERROR_STOP=1`; setup/verification must use only a disposable course database.
- Bridge starters must remain safe without psycopg or a live database. Keep solution SQL parameterized, transactions explicit, pool/connection lifecycles bounded, and examples testable through fakes.

## Maintainer code

- Shared Python tooling lives under `src/ds60sqlpy/`; `scripts/` contains thin entry points and deterministic notebook/catalog maintenance; bridge validation lives under `bridge/scripts/`.
- Ruff line length is 100. Strict mypy and pytest cover shared tooling, the
  core bridge, and the Python and bridge professional solutions/tests as
  configured in `pyproject.toml`.
- Do not hand-edit `curriculum/catalog.json`, `START_HERE.html`, `docs/practice-coverage.md`, or generated Day 46-60 solution notebooks; update their inputs and regenerate. Keep `curriculum/practice_baseline.json` immutable after the initial audit.
- The optional portal stays loopback-only with token-protected same-origin writes, sensitive-path blocking, and fixed VS Code/Jupyter actions. Static HTML must remain self-contained and usable without a server.
- Preserve unrelated work and do not commit environments, caches, secrets, checkpoints, progress, MLflow runs, or generated outputs.
