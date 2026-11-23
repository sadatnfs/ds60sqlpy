---
phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs
plan: 01
subsystem: ui
tags: [classroom-guide, tour, python, playwright, learner-state]

requires: []
provides:
  - Disposable-browser assertions for Python solution walkthrough behavior and learner-state preservation
  - Clarified local startup guidance and no-selection-safe lesson tours
affects: [Phase 1 plans 01-02 through 01-05, classroom guide, Python walkthroughs]

actuals:
  tokens: 5323
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - Compare visible and persisted learner state around guidance-only actions.

key-files:
  created: []
  modified:
    - scripts/check_classroom_browser.py
    - scripts/check_classroom_ui.mjs
    - src/ds60sqlpy/assets/classroom-guide.js
    - src/ds60sqlpy/assets/classroom.html

key-decisions:
  - "A tour request without an active lesson explains how to proceed instead of choosing a default subject."
  - "Keep the existing Docker Hub instruction unchanged; document only source-verified local startup."

requirements-completed: []

coverage:
  - id: D1
    description: "Python solution walkthrough assertions verify the dedicated trace request and learner-state invariance."
    requirement: WALK-04
    verification:
      - kind: other
        ref: "python3 -m py_compile scripts/check_classroom_browser.py; uv run --no-sync ruff check scripts/check_classroom_browser.py"
        status: pass
      - kind: e2e
        ref: "Disposable classroom browser acceptance; unavailable because the prepared browser runtime and CLASSROOM_URL are absent."
        status: unknown
    human_judgment: true
    rationale: "The browser assertions were added but could not be exercised against a disposable classroom."
  - id: D2
    description: "The manual and tour preserve navigation and learner state, including safe no-selection entry."
    requirement: GUIDE-01
    verification:
      - kind: unit
        ref: "node scripts/check_classroom_ui.mjs#tour entry without a selected lesson"
        status: pass
      - kind: e2e
        ref: "Disposable classroom browser acceptance; unavailable because the prepared browser runtime and CLASSROOM_URL are absent."
        status: unknown
    human_judgment: true
    rationale: "Manual and selected-lesson tour lifecycle assertions require a real browser run."
  - id: D3
    description: "Tour entry with no lesson selection does not navigate, open a lesson, or submit execution."
    requirement: GUIDE-02
    verification:
      - kind: unit
        ref: "node scripts/check_classroom_ui.mjs#tour entry without a selected lesson"
        status: pass
      - kind: e2e
        ref: "Disposable classroom browser acceptance; unavailable because the prepared browser runtime and CLASSROOM_URL are absent."
        status: unknown
    human_judgment: true
    rationale: "The no-selection path is regression-tested in the UI harness, but the planned real-browser acceptance remains outstanding."

duration: "unknown; resumed execution start time was not captured"
completed: 2026-11-23
status: halted
---

# Phase 1 Plan 1: Guide and Walkthrough Qualification Summary

**Local guide and tour changes are regression-tested, but the plan is halted pending its required disposable-browser acceptance.**

## Performance

- **Duration:** Unknown; execution resumed from an earlier turn.
- **Started:** Not captured.
- **Completed:** 2026-11-23T23:57:51Z.
- **Tasks:** 2 implementation tasks completed; real-browser acceptance remains outstanding.
- **Files modified:** 4.

## Accomplishments

- Added a browser-check path for Python solution step-through that distinguishes `action: "step-through"` and `purpose: "solution"` from ordinary Run, checks for rendered trace steps, and compares lesson selection, editor source, notes/session, exercise progress, saved pad, pad history, and receipts before and after the trace.
- Clarified local initialization prerequisites and the `doctor` then classroom startup sequence without changing the existing Docker Hub instruction.
- Made tour entry without a selected lesson report that a lesson must be selected rather than switching tracks. Added coverage for no-selection home/manual entry and browser checks for manual routes, tour lifecycle, and return to a previously selected lesson.
- The UI regression harness passed all 95 checks. Python compilation, Ruff, JavaScript syntax, and whitespace checks passed.

## Task Commits

1. **Task 1: Trace one Python solution walkthrough through the real desktop classroom** - `31b78ce8` (`test(01-01): cover Python solution walkthrough with browser assertions`)
2. **Task 2: Qualify manual entry points and make every tour route selection-neutral** - `28bf5471` (`fix(01-01): keep lesson tours selection-neutral`)

## Files Created/Modified

- `scripts/check_classroom_browser.py` - Added walkthrough state snapshots plus manual, tour, and no-selection browser assertions.
- `scripts/check_classroom_ui.mjs` - Added a fast regression test for no-selection home and manual tour requests.
- `src/ds60sqlpy/assets/classroom-guide.js` - Removed fallback subject selection from tour entry.
- `src/ds60sqlpy/assets/classroom.html` - Clarified verified local setup instructions.

## Decisions Made

- Preserve the current manual route, entry points, section anchors, and tour overlay; change only the no-selection behavior and local startup explanation.
- Keep Docker Hub guidance untouched and do not claim its target is verified.
- Do not install browser packages or substitute a learner classroom for the plan's disposable target.

## Deviations from Plan

**1. Added an offline UI regression assertion in `scripts/check_classroom_ui.mjs`.**
- **Found during:** Task 2 (manual and tour qualification)
- **Issue:** The plan's required prepared browser environment was unavailable, leaving no runnable test for the no-selection regression in the available local harness.
- **Fix:** Extended the existing UI harness with a narrow test proving home/manual no-selection requests stay on the current screen and make no lesson-open or track-switch calls.
- **Files modified:** `scripts/check_classroom_ui.mjs`
- **Verification:** `node scripts/check_classroom_ui.mjs` passed with 95 checks.
- **Committed in:** `28bf5471`

**Total deviations:** 1 auto-fixed (1 verification coverage addition). **Impact:** Adds fast local evidence but does not replace the required browser acceptance.

## Issues Encountered

- The prepared browser Python, Chromium command, and disposable `CLASSROOM_URL` were unavailable. Per the plan, browser dependencies were not installed and no learner classroom was used. The real-browser acceptance gate is **unavailable**, not passed.

## User Setup Required

None.

## Next Phase Readiness

- Plan 01-01 is **halted** until a prepared disposable classroom browser environment and `CLASSROOM_URL` are available. Run the exact browser command from the plan, review its receipt report, then re-summarize this plan as complete only if the acceptance criteria pass.
- Dependent Phase 1 waves remain blocked. `GUIDE-01`, `GUIDE-02`, and `WALK-04` remain pending; this summary does not mark them complete.

## Self-Check: FAILED

- Local UI regression, Python compilation, Ruff, JavaScript syntax, and whitespace checks passed.
- The required disposable-browser acceptance could not run because its prepared runtime and target URL are unavailable. Real-browser acceptance criteria remain unverified, so the plan is halted.

---
*Phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs*
*Completed: 2026-11-23*
