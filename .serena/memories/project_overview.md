# ds60sqlpy project overview

- Purpose: a self-paced, beginner-friendly Python/data-science, PostgreSQL, and Python/PostgreSQL engineering curriculum that works on Windows, macOS, and Linux. The historical day count is an ordering aid, not a deadline.
- Learner entry points: `README.md`, generated `START_HERE.html`, and one
  deterministic rendered page per catalog lesson under `lesson-pages/`;
  human navigation: `docs/curriculum-map.md`; generated machine inventory:
  `curriculum/catalog.json`. Linked non-catalog Markdown/SQL sources render
  under `reference-pages/`, so generated navigation never opens raw local
  source. Static pages are self-contained/read-only and usable over `file://`;
  static completion stays on `START_HERE.html`.
  `scripts/learning_portal.py` optionally serves the pages on loopback,
  synchronizes ignored `.learning/progress.json`, reveals the lesson-level
  completion control, and exposes only catalog-resolved VS Code/Jupyter
  actions.
- Windows front door: double-click `START_DS60.cmd`. Its PowerShell 5.1
  orchestrator discovers or prepares either supported `.venv` layout, checks
  VS Code/PostgreSQL/Jupyter/kernel readiness, runs the doctor, and opens the
  private portal. Connected setup requires acknowledgement; diagnostics are
  read-only.
- Python track: 60 learner notebooks, 60 companion guides, 60 Markdown
  solutions, and 60 runnable solution notebooks under `python/ds-60day/`, plus
  10 named professional modules under `python/professional/`. All 120 core
  notebooks are normalized to nbformat 4.5, kernel name `ds60sqlpy`, display
  name `Python (ds60sqlpy)`, stable cell IDs, cleared outputs, and
  course/capability tags.
- SQL track: `sql/postgres-60day/00_setup.sql` creates deterministic `training`
  data; `00_verify.sql` enforces invariants; 60 core learner scripts, guides,
  Markdown solutions, and executable solution files target PostgreSQL 16+
  (canonical CI PostgreSQL 17). Two relational-foundations modules and 10
  advanced/specialization modules live under `sql/professional/`. Most lessons
  roll back. Days 52-54 are the explicit stateful `dwh` sequence.
- Engineering bridge: eight core lessons under `bridge/` connect Python and
  PostgreSQL through parameterized Psycopg queries, transactions, pooling, ETL,
  data quality, observability, testing, and a capstone. Four professional
  modules under `bridge/professional/` add PostgreSQL Jupyter magics,
  migration delivery, local AI application engineering, and analytics
  engineering. Starters remain runnable without a database; fake-backed tests
  validate the solution contracts.
- Course tooling: importable package under `src/ds60sqlpy/`; source-checkout
  CLI `python scripts/course.py` provides doctor, catalog, validation,
  progress, portal, and PostgreSQL runners. `scripts/audit_practice.py`
  enforces each lesson surface's `max(6, 2 x immutable baseline)` practice
  target. `scripts/build_course_guide.py` is the only source for
  `START_HERE.html`; `src/ds60sqlpy/lesson_reader.py` and
  `scripts/build_lesson_readers.py` own the tracked `lesson-pages/` and
  `reference-pages/` output. `bridge/scripts/validate_bridge.py` adds
  bridge-specific checks.
- Guided SQL flow: a SQL reader's private action calls the catalog-restricted
  generator in `src/ds60sqlpy/sql_notebook.py`, creates an editable notebook
  and SQL copy beneath ignored `.learning/sql/<lesson-id>/`, and launches that
  exact notebook. It preserves existing work, uses fixed non-shell `psql -f`,
  accepts only `advanced_sql_training`, and separates explicit database reset
  confirmation from lesson execution. The checked-in `bridge-jupyter-01`
  notebook remains the separate JupySQL-magics lesson.
- Notebook maintenance: `scripts/normalize_notebooks.py`, `scripts/build_solution_notebooks.py`, and `scripts/validate_notebooks.py` are deterministic and idempotent. Generated Day 46-60 solution notebooks come from their Markdown sources.
- Cross-platform setup: `scripts/setup.ps1` on Windows and `scripts/setup.sh` on macOS/Linux create the ignored local `.venv` and register `Python (ds60sqlpy)`. Optional-dependency profiles live in `pyproject.toml`; convenience aliases live under `requirements/`; `uv.lock` is the reviewed cross-platform resolution.
- Agent guidance: root `AGENTS.md`, nested track guidance, and `.agents/skills/guide-ds60sqlpy-learning/` support hint-first Codex tutoring, learner-machine-aware setup, assessment, and opt-in local progress.
- Automation: `.github/workflows/ci.yml` checks Python 3.11/3.12 across Ubuntu,
  Windows, and macOS, notebook smoke execution, all professional modules,
  common credential patterns, and PostgreSQL 17 course paths.
- Local environments, caches, `mlruns/`, outputs under `artifacts/`, checkpoints, and `.learning/` progress are ignored and must never be committed.
