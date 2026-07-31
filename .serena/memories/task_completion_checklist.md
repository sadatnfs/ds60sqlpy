# Task completion checklist

1. Read root `AGENTS.md` and the closest nested guidance; inspect `git status --short --branch` and preserve unrelated work.
2. Keep each learner artifact, companion guide, solution artifacts, builder metadata, and generated catalog aligned. Meet the immutable practice target `max(6, 2 x baseline)` on learner, guide, and explanatory-solution surfaces and regenerate `docs/practice-coverage.md`. For bridge work, keep starters, guides, executable solutions, reasoning guides, and fake-backed tests aligned.
3. Regenerate `curriculum/catalog.json`, `START_HERE.html`, and affected
   `lesson-pages/*.html`/`reference-pages/**/*.html` after artifact, metadata,
   or rendered local-link changes. Require
   `scripts/build_course_guide.py --check`,
   `scripts/build_lesson_readers.py --check`, and
   `python scripts/course.py validate --all` to pass.
4. For notebook changes, run `scripts/normalize_notebooks.py --check`, `scripts/build_solution_notebooks.py --check` when generated Day 46-60 solutions are affected, and `scripts/validate_notebooks.py`; execute the relevant fresh-kernel smoke path when behavior changed.
5. Keep notebooks nbformat 4.5 with unique stable IDs, kernel name `ds60sqlpy`, display name `Python (ds60sqlpy)`, course tags, cleared outputs, ignored artifact paths, and no hidden execution order.
6. For SQL changes, start from a fresh disposable database, run `00_setup.sql`
   and `00_verify.sql` with `psql -X -v ON_ERROR_STOP=1`, then execute affected
   prerequisites/successors. For repository-wide changes, run all 72 learner
   scripts and all 72 executable solutions. Preserve the Days 52-54 stateful
   sequence and verify that professional modules leave no roles, schemas,
   extensions, or replication objects behind.
7. For bridge changes, run `python bridge/scripts/validate_bridge.py`, fake-backed pytest, starter offline execution, and solution import checks without requiring psycopg or a live database unless the lesson explicitly tests integration.
8. Check Windows PowerShell and POSIX command variants; native command failures in PowerShell must be surfaced. Do not put Bash syntax in PowerShell blocks. Use repository-relative paths and `pathlib`.
9. Preserve offline-after-bootstrap behavior. Seaborn first-run cached downloads are accepted and disclosed; other network/model/map work must be explicit and tagged, with a fallback where practical.
10. Run Ruff, Ruff formatting, strict mypy, pytest, Markdown-link/catalog
    validation, the practice audit, both generated HTML drift checks,
    `git diff --check`, JSON/YAML/TOML/Compose syntax checks, and
    `uv lock --check` proportionally to the change. Learner-entry changes must
    run `test_course_guide.py`, `test_lesson_reader.py`, `test_portal.py`,
    `test_sql_notebook.py`, and `test_windows_startup.py`.
11. Portal changes must test loopback/token/origin/path/launch allowlist
    boundaries while preserving static `file://` use. Browser QA must check a
    Python, SQL, and bridge rendered reader, tab/keyboard behavior, rendered
    Markdown/SQL references, dashboard-only static completion, loopback
    completion, no raw source page, desktop/narrow layouts, and no unexpected
    network request.
12. Do not commit `.venv`, `__pycache__`, tool caches, notebook checkpoints,
    downloaded data/models, secrets, `.env`, learner progress, generated
    `.learning/sql/` notebooks, or `mlruns/`. Keep tracked
    `START_HERE.html`/`lesson-pages/`/`reference-pages/`; they are maintained
    outputs.
13. Report evidence precisely: distinguish structural validation, smoke
    execution, full execution, offline validation, and untested
    platform/heavy surfaces. For guided SQL notebooks, distinguish generation,
    Jupyter launch, explicit database preparation, lesson execution, and
    verification.
14. Before handoff, inspect the final diff, update maintained
    docs/AGENTS/Serena memories when behavior changed, and state any remaining
    limitation explicitly. Run Serena indexing/health checks after semantic
    source changes when available; remove the generated `.serena/cache/` again
    before preparing a source-only USB copy.
