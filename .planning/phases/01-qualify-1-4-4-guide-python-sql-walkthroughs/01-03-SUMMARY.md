---
phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs
plan: 03
subsystem: execution
tags: [step-through, sql, planner, walkthrough, postgresql, ci]

requires:
  - 01-02
provides:
  - An explicit unsupported result for SQL the clause planner cannot split
  - Offset and live PostgreSQL tests for SQL walkthroughs
  - Repaired CI lint, type and published-link checks
affects: [Phase 1 plans 01-04 and 01-05, SQL walkthroughs, CI]

actuals:
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Planner fallbacks return `SqlPlan(statement, start, (), UNSUPPORTED_SQL)`, and the runner returns before it creates a tempdir or starts a worker."

key-files:
  created: []
  modified:
    - src/ds60sqlpy/step_through.py
    - src/ds60sqlpy/execution.py
    - src/ds60sqlpy/assets/classroom.html
    - scripts/check_classroom_browser.py
    - tests/test_execution.py

key-decisions:
  - "Every `_Fallback` path now reports unsupported, not only clause-order errors. A probe found 14 raise sites and 0 of 1,491 lesson SQL statements reach them, so learners lose no walkthroughs today."
  - "The unsupported message is general: it tells learners to use Run and lists the clause order to check if Run also fails."
  - "The existing UI already renders `unsupported`, so the front end was not changed."
  - "The optional time limit is passed through unchanged so `_execute` applies the default in one place."

requirements-completed: [WALK-02]

coverage:
  - id: D1
    description: "SQL the planner cannot split returns an explicit unsupported result with no steps and no database work."
    requirement: WALK-02
    verification:
      - kind: unit
        ref: "tests/test_execution.py::test_plan_sql_fallback_is_explicitly_unsupported"
        status: pass
    human_judgment: false
    rationale: "Failed before the fix (the planner returned one whole-query step) and passes after it."
  - id: D2
    description: "Clause offsets slice the original source exactly, including after astral characters."
    requirement: WALK-02
    verification:
      - kind: unit
        ref: "tests/test_execution.py::test_step_through_sql_offsets_match_original_source"
        status: pass
    human_judgment: false
    rationale: "Offsets are code points computed on the server; an emoji before the statement keeps every slice correct."
  - id: D3
    description: "Live walkthrough steps return the expected rows, reject writes, and leave tables and sequences unchanged."
    requirement: WALK-02
    verification:
      - kind: integration
        ref: "tests/test_execution.py::test_live_step_through_sql_results_and_rejection_preserve_database_state"
        status: pass
    human_judgment: false
    rationale: "Passed locally against a disposable postgres:17 container and runs in the CI PostgreSQL 17 job."

duration: "about 2 hours"
completed: 2026-11-24
status: complete
---

# Phase 1 Plan 3: SQL Planner Fallback and Offsets Summary

**SQL the walkthrough planner cannot split now reports a clear unsupported message rather than a misleading single step, and clause offsets and live database safety are pinned by tests.**

## Performance

- **Completed:** 2026-11-24.
- **Tasks:** 3.
- **Files modified:** 5.

## Accomplishments

- `plan_sql` now returns an empty plan with `UNSUPPORTED_SQL` for every `_Fallback` path. The message reads: "Step-through can't split this query into clauses, so use Run for it. If Run reports an error, check that the clauses are complete and in order: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT."
- Added three tests:
  - The fallback test, which failed first.
  - The source offsets test, which includes an emoji before the statement.
  - A live PostgreSQL test that checks each step's rows and confirms rejected writes and `nextval` leave the sentinel table and sequence unchanged.
- Repaired the CI failures that blocked the last pushed checkpoint:
  - 12 ruff findings in `step_through.py`.
  - 3 mypy errors: in `execution.py`, `sql_response` and the browser checker.
  - 3 `missing_fragment` link failures, fixed by adding `id="how-it-works"` to the manual header.

## Impact Evidence

- A throwaway probe planned every SQL statement in the course: 0 of 1,491 reached `_Fallback`, so no existing lesson loses its walkthrough.

## Verification

- Focused tests, `tests/test_learning_lab.py` and `tests/test_execution.py`, run without a database: 65 passed and 16 skipped (the database-only cases).
- Live run of `-k step_through` against a disposable `postgres:17` container: 6 passed, including the new live test.
- `ruff check` across the full CI scope, `ruff format --check` and full `mypy` over 409 files: all clean.
- `node scripts/check_classroom_ui.mjs`: 95 checks passed.
- `scripts/check_published_links.py`: 0 failures.

## Task Commits

1. **Fallback fix and tests** - `f9ce1c19` (`fix(01-03): reject unsupported SQL walkthrough fallback`)
2. **CI repairs** - `094358cc` (`fix(ci): restore lint, type and published link checks`)

## Deviations from Plan

- The fix applies to all 14 fallback raise sites rather than only clause-order errors, so the message was made general.
- The CI lint, type and link repairs were added because they blocked the pushed checkpoint.

## Deferred

- The browser cursor offset comes from CodeMirror, which counts UTF-16 units, while server offsets count code points. An astral character before the cursor in the editor can therefore shift the active clause by one position. This is rare and is left for a later UI pass.
- A local `-k live` run also hit `psql is not on PATH` for the whole-lesson test. That is environmental: CI installs `postgresql-client`.

## Next Phase Readiness

Plan 01-04 (the SQL safety boundary at LabServer) can proceed.
