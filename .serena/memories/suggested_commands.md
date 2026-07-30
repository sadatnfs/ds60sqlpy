# Suggested commands

Run from the repository root. Prefer the repository interpreter:
`.venv/bin/python` on macOS/Linux. On Windows, use the exact path printed by
the discovery bootstrap: `.venv\Scripts\python.exe` for standard `venv` or
`.venv\python.exe` for its conda-prefix fallback.

## Setup and learner navigation

- Windows core/discovery: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; & .\scripts\bootstrap_windows.ps1`
- Windows advanced: `& .\scripts\bootstrap_windows.ps1 -Profile Advanced`
- macOS/Linux core: `bash scripts/setup.sh`
- macOS/Linux advanced: `bash scripts/setup.sh --advanced`
- Environment: `.venv/bin/python scripts/course.py doctor`
- Inventory: `.venv/bin/python scripts/course.py catalog`
- Track inventory: add `--track python`, `--track sql`, or `--track bridge`
- Progress: `.venv/bin/python scripts/course.py progress show`
- Private progress portal: `.venv/bin/python scripts/learning_portal.py`
- Static portal only: open `START_HERE.html`; its progress stays in browser localStorage

## Fast validation

- `.venv/bin/python scripts/course.py validate --all`
- `.venv/bin/python scripts/audit_practice.py`
- `.venv/bin/python scripts/build_course_guide.py --check`
- `.venv/bin/python scripts/scan_secrets.py --history`
- `.venv/bin/python scripts/validate_notebooks.py`
- `.venv/bin/python scripts/normalize_notebooks.py --check`
- `.venv/bin/python scripts/build_solution_notebooks.py --check`
- `.venv/bin/python bridge/scripts/validate_bridge.py`
- `.venv/bin/ruff check --no-cache src scripts tests bridge python/professional`
- `.venv/bin/ruff format --check --no-cache src scripts tests bridge python/professional`
- `.venv/bin/mypy --cache-dir /tmp/ds60sqlpy-mypy-cache`
- `.venv/bin/pytest -p no:cacheprovider`
- `git diff --check`

Use the selected Windows environment's `python.exe -m TOOL` equivalent in
PowerShell. On Windows, choose a writable temporary mypy cache directory rather
than `/tmp`.

## Notebook execution

- Offline smoke subset: `.venv/bin/python scripts/validate_notebooks.py --smoke`
- Explicit fallback kernel for a maintainer machine without the registered course kernel: add `--kernel-name python3`
- JupyterLab: `.venv/bin/python -m jupyterlab python/ds-60day/notebooks`
- Standard checked-in kernel: name `ds60sqlpy`, display name `Python (ds60sqlpy)`

## PostgreSQL

- Compose server: `docker compose up -d postgres`
- Compose setup: `docker compose run --rm sql-runner -f sql/postgres-60day/00_setup.sql`
- Compose verify: `docker compose run --rm sql-runner -f sql/postgres-60day/00_verify.sql`
- Local setup plus verification: `.venv/bin/python scripts/course.py sql setup --yes`
- Run one day: `.venv/bin/python scripts/course.py sql run 1`
- All learner lessons from reset: `.venv/bin/python scripts/course.py sql --quiet all --reset`
- All executable solutions from reset: `.venv/bin/python scripts/course.py sql --quiet solutions --reset`
- Direct psql must use `psql -X -v ON_ERROR_STOP=1 ...`.

## Generated inventory and lock

- Regenerate catalog: `.venv/bin/python scripts/build_catalog.py`
- Check lock: `UV_CACHE_DIR=/tmp/ds60sqlpy-uv-cache uv lock --check`
- Reproduce CI core: `uv sync --frozen --extra notebooks --extra data --extra bridge --extra quality --extra professional --extra sql-notebooks`
- Install every optional lesson dependency only for a full maintainer audit: `uv sync --frozen --all-extras`
- After an all-extras install: `uv run --no-sync python scripts/check_advanced_imports.py`

## Git and search

- `git status --short --branch`
- `rg --files`
- `rg -n "PATTERN" python sql bridge docs src scripts tests requirements`

Never run `00_setup.sql` or Days 52-54 against a production/shared database; they drop course-owned schemas.
