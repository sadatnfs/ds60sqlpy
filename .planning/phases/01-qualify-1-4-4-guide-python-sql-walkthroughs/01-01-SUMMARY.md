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
  tasks: 3
  commits: 3

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
    - src/ds60sqlpy/assets/classroom.css

key-decisions:
  - "A tour request without an active lesson explains how to proceed instead of choosing a default subject."
  - "Keep the existing Docker Hub instruction unchanged; document only source-verified local startup."

requirements-completed: [WALK-04, GUIDE-01, GUIDE-02]

coverage:
  - id: D1
    description: "Python solution walkthrough assertions verify the dedicated trace request and learner-state invariance."
    requirement: WALK-04
    verification:
      - kind: other
        ref: "python3 -m py_compile scripts/check_classroom_browser.py; uv run --no-sync ruff check scripts/check_classroom_browser.py"
        status: pass
      - kind: e2e
        ref: "scripts/check_classroom_browser.py against disposable project ds60-phase1-browser (Chromium 156.0.8078.4); receipts work/phase1-browser-receipts.json, 17/17 checks, exit 0"
        status: pass
    human_judgment: false
    rationale: "The real-browser check exercises the dedicated solution trace request and compares learner state before and after."
  - id: D2
    description: "The manual and tour preserve navigation and learner state, including safe no-selection entry."
    requirement: GUIDE-01
    verification:
      - kind: unit
        ref: "node scripts/check_classroom_ui.mjs#tour entry without a selected lesson"
        status: pass
      - kind: e2e
        ref: "scripts/check_classroom_browser.py against disposable project ds60-phase1-browser (Chromium 156.0.8078.4); receipts work/phase1-browser-receipts.json, 17/17 checks, exit 0"
        status: pass
    human_judgment: false
    rationale: "Manual routes, tour start, dismiss, restart and completion pass in a real browser without learner-state loss."
  - id: D3
    description: "Tour entry with no lesson selection does not navigate, open a lesson, or submit execution."
    requirement: GUIDE-02
    verification:
      - kind: unit
        ref: "node scripts/check_classroom_ui.mjs#tour entry without a selected lesson"
        status: pass
      - kind: e2e
        ref: "scripts/check_classroom_browser.py against disposable project ds60-phase1-browser (Chromium 156.0.8078.4); receipts work/phase1-browser-receipts.json, 17/17 checks, exit 0"
        status: pass
    human_judgment: false
    rationale: "Both the UI harness and the real browser confirm no-selection tour entry stays put and requests no execution."

duration: "unknown; resumed execution start time was not captured"
completed: 2026-11-24
status: complete
---

# Phase 1 Plan 1: Guide and Walkthrough Qualification Summary

**The Python solution walkthrough, manual and tour are qualified in a real Chromium browser against a disposable classroom: 17 of 17 checks pass.**

## Performance

- **Duration:** Unknown; execution spanned several resumed sessions.
- **Started:** Not captured.
- **Completed:** 2026-11-24.
- **Tasks:** 2 implementation tasks plus the real-browser acceptance gate.
- **Files modified:** 5.

## Accomplishments

- Added a browser check for Python solution step-through that distinguishes `action: "step-through"` and `purpose: "solution"` from an ordinary Run, checks for rendered trace steps, and compares lesson selection, editor source, notes and session, exercise progress, saved pad, pad history and receipts before and after the trace.
- Clarified local initialization prerequisites and the `doctor`, then classroom startup sequence, without changing the Docker Hub instruction.
- Tour entry without a selected lesson now explains that a lesson must be selected instead of switching tracks. Browser checks cover manual routes, the tour lifecycle and returning to a previously selected lesson.
- The first-visit tour offer wraps inside the workspace header, so it no longer overflows narrow viewports.
- Real-browser acceptance passed against the disposable project `ds60-phase1-browser`, rebuilt from the current tree with fresh volumes: Chromium 156.0.8078.4, 17/17 checks, checker exit 0, receipts `complete: true`.

## Browser Evidence

Receipts in `work/phase1-browser-receipts.json` (scope `classroom-and-fixtures`):

- All 40 subjects are selectable; home fits desktop and narrow viewports
- Day 02 setup steps retain 1, 2, 3, 4 across commands and paragraphs
- Declining the optional tour preserves the lesson and learner state
- Python solution step-through uses a distinct request and preserves learner state
- The manual explains its controls and returns to the same lesson
- The lesson tour starts, dismisses, restarts and completes without data loss
- Starting a tour from home returns to the previously selected lesson
- Fresh Python execution and receipts; readable output and prose in both appearances
- Python, SQL and module source, notes and results remain isolated across switching
- Textbook renders MathML and syntax colors; chapter fits a narrow viewport
- No-selection home and manual tour entries stay put and request no execution
- A fresh browser restores server-saved progress, notes, pads and run results
- Saved Plotly SVGs fit desktop, mobile and reopened panels; original JSON stays exact
- js-029, js-030 and js-031 completed references pass real browser interaction checks
- No uncaught JavaScript exceptions, HTTP failures or external requests

## Task Commits

1. **Task 1: Trace one Python solution walkthrough through the real desktop classroom** - `31b78ce8` (`test(01-01): cover Python solution walkthrough with browser assertions`)
2. **Task 2: Qualify manual entry points and make every tour route selection-neutral** - `28bf5471` (`fix(01-01): keep lesson tours selection-neutral`)
3. **Browser acceptance fixes** - `fd93fcfa` (`fix(01-01): pass disposable browser acceptance`)

## Files Created/Modified

- `scripts/check_classroom_browser.py` - Walkthrough state snapshots plus manual, tour and no-selection browser assertions; the subject count comes from the catalog.
- `scripts/check_classroom_ui.mjs` - Fast regression test for no-selection home and manual tour requests.
- `src/ds60sqlpy/assets/classroom-guide.js` - Removed fallback subject selection from tour entry.
- `src/ds60sqlpy/assets/classroom.html` - Clarified verified local setup instructions.
- `src/ds60sqlpy/assets/classroom.css` - The tour offer wraps and stays within its container.

## Decisions Made

- Preserve the current manual route, entry points, section anchors and tour overlay; change only the no-selection behavior and the local startup explanation.
- Keep Docker Hub guidance untouched and do not claim its target is verified.
- Run browser acceptance only against a disposable project, never the learner's `ds60-classroom` project or volumes.

## Deviations from Plan

**1. Added an offline UI regression assertion in `scripts/check_classroom_ui.mjs`.**
- **Found during:** Task 2
- **Issue:** No fast local test covered the no-selection regression.
- **Fix:** A narrow harness test proves home and manual no-selection requests stay on the current screen and make no lesson-open or track-switch calls.
- **Committed in:** `28bf5471`

**2. Prepared a containerized browser runtime instead of a preinstalled `work/browser-env`.**
- **Found during:** Browser acceptance
- **Issue:** The plan assumed a prepared browser environment. None existed, and the user asked to continue end to end.
- **Fix:** Ran the unchanged checker inside `mcr.microsoft.com/playwright/python:v1.64.1-noble` with Playwright 1.64.1 installed from the Microsoft package feed into an external cache. Nothing was installed on the host or in the repository. The container joins the disposable postgres network namespace and forwards the published host port to the lab so the lab's Host-header check sees the real public address.
- **Verification:** 17/17 browser checks passed.

**3. [Rule 1 - Bug] The no-selection check hardcoded four subject cards.**
- **Found during:** Browser acceptance
- **Issue:** The assertion added in `28bf5471` expected `4` cards, but the catalog has 40 subjects.
- **Fix:** Count from `len(SUBJECTS)`.
- **Committed in:** `fd93fcfa`

**4. [Rule 1 - Bug] The first-visit tour offer overflowed a 390px viewport by 5px.**
- **Found during:** Browser acceptance (saved Plotly viewer overflow check)
- **Issue:** `#tour-offer` is an inline flex row inside the workspace header and could not wrap.
- **Fix:** `.tour-offer` gains `flex-wrap: wrap` and `max-width: 100%`.
- **Committed in:** `fd93fcfa`

**5. [Rule 3 - Blocking] Repository formatters flagged plan changes.**
- **Issue:** `ruff format` reflowed the checker and Prettier reflowed the startup paragraph in `classroom.html`.
- **Fix:** Applied the repository formatters; whitespace-only changes.
- **Committed in:** `fd93fcfa`

**Total deviations:** 5 (1 coverage addition, 1 environment substitution, 3 auto-fixed). **Impact:** No scope change; the acceptance criteria were verified as written.

## Issues Encountered

- The lab container shares the postgres container's network namespace and has no address of its own, so the browser container must join that namespace rather than resolve a `lab` hostname.

## User Setup Required

None.

## Next Phase Readiness

- Waves 2 through 5 are unblocked. `WALK-04`, `GUIDE-01` and `GUIDE-02` are verified.
- Later browser gates reuse the same disposable project after `./classroom --rebuild` for source or asset changes.

## Self-Check: PASSED

- Real-browser acceptance: 17/17, exit 0.
- `node scripts/check_classroom_ui.mjs`: 95 checks passed.
- Ruff check and format, Prettier (web language pass) and `git diff --check` passed.

---
*Phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs*
*Completed: 2026-11-24*
