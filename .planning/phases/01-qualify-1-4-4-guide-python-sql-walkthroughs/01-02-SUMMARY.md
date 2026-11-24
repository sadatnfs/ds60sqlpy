---
phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs
plan: 02
subsystem: execution
tags: [step-through, python, trace, walkthrough, contract-tests]

requires:
  - 01-01
provides:
  - Contract tests for the real PadRunner Python trace path on both trace backends
affects: [Phase 1 plans 01-03 through 01-05, Python walkthroughs]

actuals:
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - Parametrize trace contract tests over the `auto` and `settrace` backends through `stepping.PYTHON_TRACE_BACKEND`.

key-files:
  created: []
  modified:
    - tests/test_execution.py

key-decisions:
  - "The worker already satisfies WALK-01, so step_through.py was left unchanged."
  - "Line events record state before the statement on that line runs; tests assert exactly this convention and nothing stronger."
  - "Output truncation stays visible as the notice text only; no structured flag was added to the response shape."

requirements-completed: [WALK-01]

coverage:
  - id: D1
    description: "Python walkthroughs return source-linked line, call, return and exception events with stack locals and cumulative output."
    requirement: WALK-01
    verification:
      - kind: unit
        ref: "tests/test_execution.py::test_step_through_python_has_source_linked_events_and_locals[auto,settrace]"
        status: pass
    human_judgment: false
    rationale: "The test drives PadRunner.step_through on a real program and asserts line numbers, events, function frames, locals and monotonic output lengths."
  - id: D2
    description: "Step count, output size, errors and elapsed time stay bounded and observable."
    requirement: WALK-01
    verification:
      - kind: unit
        ref: "tests/test_execution.py::test_step_through_python_reports_output_step_limits_and_errors[auto,settrace]"
        status: pass
    human_judgment: false
    rationale: "Covers ZeroDivisionError at line 3, a nested KeyError, the 400-step limit with no error, and the 64 KB output cap with its notice."

duration: "about 30 minutes"
completed: 2026-11-24
status: complete
---

# Phase 1 Plan 2: Python Trace Contract Summary

**The Python walkthrough trace is now pinned by contract tests on both trace backends; the existing worker passed without changes.**

## Performance

- **Completed:** 2026-11-24.
- **Tasks:** 2.
- **Files modified:** 1 (`tests/test_execution.py`).

## Accomplishments

- Added `test_step_through_python_has_source_linked_events_and_locals`, which checks source-linked `line`, `call`, `return` and `exception` events, per-frame stacks and locals, the `<module>` entry at line 1, and output lengths that only grow and end at the full output length.
- Added `test_step_through_python_reports_output_step_limits_and_errors`, which checks a structured `ZeroDivisionError` at line 3 with output before the failure kept, a nested `KeyError`, the 400-step limit (`step_limit_reached` true, `error` None) and the 65,536-character output cap with its notice.
- Both tests run on the `auto` and `settrace` backends (4 cases).

## Mutation Evidence

- Reporting `line + 1` in the worker failed all 4 cases.
- Forcing `step_limit_reached` to false in `python_response` failed 2 cases.
- Both mutations were reverted; `src/ds60sqlpy/step_through.py` is unchanged.

## Verification

- `env -u DS60_TEST_DATABASE_URL -u DS60_SQL_EXPANSION_TEST_URL -u DS60_DATABASE_URL .venv/bin/python -m pytest -n 0 tests/test_learning_lab.py tests/test_execution.py -q`: 63 passed, 15 skipped (database-only cases).
- `ruff check`, `ruff format --check` and `mypy` on `tests/test_execution.py`: clean.

## Task Commits

1. **Tasks 1 and 2: Python trace contract tests** - `2b91d8d3` (`test(01-02): qualify Python walkthrough trace contract`)

## Deviations from Plan

- No source correction was required, so `src/ds60sqlpy/step_through.py` is listed in the plan but not modified.
- Tests were parametrized over both trace backends to cover the fallback path as well as the default.

## Next Phase Readiness

Plan 01-03 (SQL planner fallback and PostgreSQL offsets) can proceed.
