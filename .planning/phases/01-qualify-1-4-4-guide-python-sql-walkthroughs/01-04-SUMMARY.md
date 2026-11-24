---
phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs
plan: 04
subsystem: execution
tags: [step-through, sql, safety, lab-server, preparation]

requires:
  - 01-03
provides:
  - A parser-first SQL walkthrough boundary in LabServer and PadRunner
  - One shared no-database reply for unsupported or empty SQL walkthroughs
affects: [Phase 1 plan 01-05, SQL walkthroughs]

actuals:
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "`stepping.sql_unsupported_response(plan)` returns the shared reply or None; callers return it before locks, preparation, folders or workers."

key-files:
  created: []
  modified:
    - src/ds60sqlpy/step_through.py
    - src/ds60sqlpy/execution.py
    - src/ds60sqlpy/lab.py
    - tests/test_learning_lab.py

key-decisions:
  - "LabServer parses SQL after the size, time limit, purpose and cursor checks, and before it takes the execution lock, so a rejected walkthrough never waits behind a running pad."
  - "PadRunner plans SQL before it creates the saved-pad folder and passes the plan to `_step_through_sql`, so each statement is parsed once on that path."
  - "Supported statements keep the existing order: course preparation, then the trace."

requirements-completed: [WALK-02]

coverage:
  - id: D1
    description: "Rejected and empty SQL walkthroughs skip course preparation, the SQL worker, run receipts and the saved-pad folder."
    requirement: WALK-02
    verification:
      - kind: unit
        ref: "tests/test_learning_lab.py::test_rejected_sql_step_through_skips_database_preparation_and_pad_path"
        status: pass
    human_judgment: false
    rationale: "Failed before the fix (preparation ran first, then PadRunner created `.learning/pads`) and passes after it, through `LabServer.action` and a direct PadRunner call."
  - id: D2
    description: "Supported SQL walkthroughs prepare the course before the trace and never take the Run or save path."
    requirement: WALK-02
    verification:
      - kind: unit
        ref: "tests/test_learning_lab.py::test_supported_sql_step_through_prepares_before_trace"
        status: pass
    human_judgment: false
    rationale: "Records the call order and forwards cursor and time limit unchanged; Run, save and receipts raise if called."

duration: "about 40 minutes"
completed: 2026-11-24
status: complete
---

# Phase 1 Plan 4: SQL Walkthrough Safety Boundary Summary

**SQL the walkthrough cannot trace is now rejected before any course preparation, folder creation or worker start, while supported statements keep preparing the course first.**

## Performance

- **Completed:** 2026-11-24.
- **Tasks:** 2.
- **Files modified:** 4.

## Accomplishments

- Added `sql_unsupported_response(plan)` to `step_through.py`. It returns the shared `{"kind": "sql", ..., "steps": [], "unsupported": ...}` reply, or None when the plan has steps.
- `LabServer._step_through` plans SQL before the execution lock and `ensure_before_run`, and returns the shared reply for unsupported or empty input.
- `PadRunner.step_through` plans SQL before it creates `.learning/pads/<lesson>` and passes the plan to `_step_through_sql`, which no longer re-parses.
- Added two tests that drive the real `LabServer.action`:
  - The rejected-SQL test, which failed first.
  - The supported-order test.

## Verification

- `tests/test_learning_lab.py` and `tests/test_execution.py` without a database: 67 passed, 16 skipped.
- Live `-k step_through` against a disposable `postgres:17` container: 8 passed.
- `ruff check`, `ruff format --check`, full `mypy` over 409 files and `git diff --check`: all clean.

## Task Commits

1. **Parser-first boundary and tests** - `72651e0b` (`fix(01-04): parse SQL walkthroughs before course preparation`)

## Deviations from Plan

- The first run showed that a direct PadRunner call also created the saved-pad folder before parsing, so the parser-first check was added there too.

## Next Phase Readiness

Plan 01-05 (SQL learner claims and browser acceptance) can proceed.
