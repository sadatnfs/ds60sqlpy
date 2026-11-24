---
phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs
plan: 05
subsystem: walkthroughs
tags: [step-through, sql, python, manual, tour, browser-acceptance]

requires:
  - 01-01
  - 01-02
  - 01-03
  - 01-04
provides:
  - SQL solution walkthroughs that replay each solution's trusted setup context
  - A friendly read-only step message pointing learners to Run
  - Real-browser preservation evidence (lesson and draft SHA-256) for every tour and solution inspection
  - 01-VERIFICATION.md with automated outcomes and the open human clarity item
affects: [Phase 2 content work, SQL walkthroughs, browser gate]

actuals:
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Solution walks send `exercise` with `purpose: solution`; the server slices the `.sql` solution before that exercise marker, inlines `\\ir` includes and replays the answer prefix inside savepoints."
    - "Worker errors map `ReadOnlySqlTransaction` to `stepping.READ_ONLY_STEP`; tests assert the constant, not a substring."
    - "`Audit.preserved(inspection, before, after)` records lesson and draft digests in the checker report's `preservation` list."

key-files:
  created:
    - .planning/phases/01-qualify-1-4-4-guide-python-sql-walkthroughs/01-VERIFICATION.md
  modified:
    - src/ds60sqlpy/exercises.py
    - src/ds60sqlpy/step_through.py
    - src/ds60sqlpy/execution.py
    - src/ds60sqlpy/lab.py
    - src/ds60sqlpy/assets/classroom-guide.js
    - src/ds60sqlpy/assets/classroom.html
    - scripts/check_classroom_browser.py
    - sql/postgres-60day/solutions/day52_solutions.md
    - tests/test_execution.py
    - tests/test_learning_lab.py

key-decisions:
  - "Step-through stays read-only. Writer blocks such as the sql-sec-01 #9 SECURITY DEFINER INSERT show a friendly message instead of being allowed to write."
  - "The trusted setup context comes from the course's own `.sql` solution file, never from learner input."
  - "Human first-time clarity is recorded as UNAVAILABLE because no reviewer was present in autopilot; automated preservation evidence is recorded as PASS."

requirements-completed: [GUIDE-01, GUIDE-02, WALK-04]

coverage:
  - id: D1
    description: "Every SQL Markdown solution block steps successfully or reports an explicit unsupported or read-only reason."
    requirement: WALK-02
    verification:
      - kind: integration
        ref: "Probe across all SQL solutions on the disposable PostgreSQL 17 classroom: 509 ok, 68 unsupported, 1 read-only"
        status: pass
    human_judgment: false
    rationale: "Step errors fell from 160 to 9, then 4, then 1; the last is a deliberate read-only block with the friendly message."
  - id: D2
    description: "Tour and solution inspections preserve the selected lesson and saved draft."
    requirement: WALK-04
    verification:
      - kind: e2e
        ref: "scripts/check_classroom_browser.py (20 of 20 PASS, preservation list with 10 matching digests)"
        status: pass
    human_judgment: false
    rationale: "Chromium 156 at 1440 x 1000 against a disposable starter classroom."
  - id: D3
    description: "A first-time learner finds the manual, setup and lesson-switching guidance clear."
    requirement: GUIDE-01
    verification:
      - kind: manual
        ref: "01-VERIFICATION.md"
        status: unavailable
    human_judgment: true
    rationale: "No human reviewer in this autopilot run; recorded as UNAVAILABLE rather than passed."

duration: "about 3 sessions"
completed: 2026-11-24
status: complete
---

# Phase 1 Plan 5: SQL Walkthrough Claims and Browser Acceptance Summary

**SQL solution walkthroughs now run against the setup each exercise expects, and a real browser shows that tours and solution walks never change the learner's lesson or draft.**

## Accomplishments

- The manual's SQL walkthrough copy now matches what is actually tested.
- Solution walkthroughs send the exercise number. The server rebuilds that exercise's trusted setup from the solution file:
  - exercise markers and numbered sections
  - `\ir` includes
  - `\gset` and other send-buffer meta-commands
  - replay of the answer's prefix
- The sql-52 Exercise 2 answer now holds the full CREATE and INSERT it depends on.
- Read-only failures show `READ_ONLY_STEP`: "This step calls something that changes data, and step-through runs read-only, so use Run to see it work."
- The browser checker records the lesson and draft SHA-256 before and after each of 10 tour and solution inspections.

## Verification

- Full pytest suite: 5694 passed, 520 skipped, 0 failed.
- Live step-through tests against PostgreSQL 17: 11 passed.
- Browser gate: 20 of 20 PASS, `checker_exit=0`, report `"complete": true`, all 10 preservation digests unchanged.
- `node scripts/check_classroom_ui.mjs`: 95 checks passed.
- `make generate`, `lint-repo`, `format-repo --check` (sql, python, web), ruff, ruff format and mypy: all clean.

## Task Commits

1. **SQL solution context and read-only message** - `1058eb73` (`feat(01-05): walk every SQL solution with its trusted setup context`)
2. **Browser preservation evidence** - `2c465c7d` (`test(01-05): record lesson and draft digests for every tour and solution inspection`)
3. **Verification record** - docs commit with this summary

## Deviations from Plan

- The plan expected only presentation checks. The probe showed that 160 SQL solution blocks failed without their setup, so solution context replay was added.
- Human first-time clarity could not be observed and is recorded as UNAVAILABLE.

## Deferred

- The CodeMirror cursor offset counts UTF-16 units while the server counts code points. ASCII lessons are unaffected; this is tracked for a later phase.

## Next Phase Readiness

Phase 1 is complete. Phase 2 can proceed.
