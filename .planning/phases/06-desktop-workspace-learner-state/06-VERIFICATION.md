---
phase: 06-desktop-workspace-learner-state
verified: 2026-11-24T05:37:19Z
status: human_needed
score: 13/14 must-haves verified
covered_files:
  - ".planning/phases/06-desktop-workspace-learner-state/06-01-PLAN.md"
  - ".planning/phases/06-desktop-workspace-learner-state/06-01-SUMMARY.md"
  - ".planning/phases/06-desktop-workspace-learner-state/06-02-PLAN.md"
  - ".planning/phases/06-desktop-workspace-learner-state/06-02-SUMMARY.md"
  - ".planning/phases/06-desktop-workspace-learner-state/06-03-PLAN.md"
  - ".planning/phases/06-desktop-workspace-learner-state/06-03-SUMMARY.md"
  - ".planning/phases/06-desktop-workspace-learner-state/06-04-PLAN.md"
  - ".planning/phases/06-desktop-workspace-learner-state/06-04-SUMMARY.md"
  - "scripts/check_classroom_browser.py"
  - "scripts/check_classroom_ui.mjs"
  - "scripts/check_classroom_workspace.py"
  - "src/ds60sqlpy/assets/classroom-editor.js"
  - "src/ds60sqlpy/assets/classroom-guide.js"
  - "src/ds60sqlpy/assets/classroom-shell.js"
  - "src/ds60sqlpy/assets/classroom.css"
  - "src/ds60sqlpy/assets/classroom.html"
  - "src/ds60sqlpy/assets/classroom.js"
  - "tests/test_classroom_browser_probe.py"
  - "tests/test_classroom_keyboard.py"
  - "tests/test_draft_backup.py"
  - "tests/test_module_ui.py"
  - "tests/test_workspace_mode.py"
  - "work/phase6-browser-receipts.json"
  - "work/phase6-restart-receipts.json"
covered_digest: "v4:sha256:30bc7fdc56834be5236eeea7b0e7e2f3a3f93bcbe5d5d6e57283b1a73ff81333"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "First-time learner confidence walkthrough (Phase 1 clarity UAT folded in by D-04; 06-UAT.md item 1). Use a fresh desktop browser profile with no saved classroom data and a person who has not used the classroom. Without coaching, they open home, pick a first lesson, find where to type, run it, read the result, then open a reading lesson (for example apache-004) and explain what the workspace strip says."
    expected: "The learner finds the editor, the Run control and the Result panel without help, and says from the strip that a reading lesson runs no code and has no Result panel. They report feeling able to continue on their own."
    why_human: "The phase goal promises learners can operate the classroom confidently. Automated checks prove the cues exist, are correct per mode and are accessible; they cannot measure whether a first-time learner understands them or feels confident."
---

# Phase 6: Desktop Workspace & Learner State Verification Report

**Phase Goal:** Learners can operate the desktop classroom confidently across its real lesson modes and continue their work without accidental execution or loss of saved evidence.
**Verified:** 2026-11-24T05:37:19Z (2026-11-23 21:37 local)
**Status:** human_needed
**Re-verification:** Yes, 2026-11-24T21:35Z after Phases 08.1, 9 and 10 changed covered files (see Re-verification below); status unchanged

## Process Notes

- **STATE.md is stale.** It still says Phase 2 is current, while ROADMAP marks the 06-01 to 06-04 plans as complete. This verification was explicitly requested for Phase 6, so it went ahead. The orchestrator should update STATE.md.
- **MVP goal format.** ROADMAP marks Phase 6 as `Mode: mvp`, but its goal is not a user story: `user-story.validate` returns `valid: false`. The MVP-mode "User Flow Coverage" table was therefore not produced. This report uses the standard goal-backward method against the three roadmap success criteria and the plan must-haves. To make the phase MVP compliant, run `/gsd-mvp-phase 6` to restate the goal, or drop the mvp mode.
- **Phase work is uncommitted.** HEAD is 5ad22de, and `git diff HEAD` shows the Phase 6 changes as working tree edits, with new test files untracked. Every summary says this is by design because the orchestrator commits. This report fingerprints the working tree.
- **Browser evidence was not rerun.** The constraints forbid starting Docker stacks, so the verifier did not rerun the browser gate. It read the receipts and checked them for consistency instead:
  - Asset mtimes are 21:20 to 21:21 local.
  - The `ds60sqlpy-lab:1.4.3` image was created at 05:30:51Z (21:30:51 local).
  - The main receipt was written at 21:33:38 local and the restart verify receipt at 21:34:49 local.
  - So the image was built after the final asset edits, and the receipts came after the image.
  - `scripts/check_classroom_workspace.py` was modified at 21:34:25, after the main receipt and before restart verify. This matches the documented restart verify fix (06-04 deviation 5) and is recorded as info.
  - A read-only check found 0 `ds60-phase6*` containers and 0 volumes.

## Re-verification (2026-11-24)

The report went stale because later phases edited files it covers: `scripts/check_classroom_ui.mjs`, `src/ds60sqlpy/assets/classroom.css`, `src/ds60sqlpy/assets/classroom.html`, `tests/test_classroom_keyboard.py`, `tests/test_module_ui.py` and `tests/test_workspace_mode.py`. Phase 08.1 (unslop chrome) made most of those edits, Phase 9 tightened the tests, and the 2.0.0 release commit `ca8ef9a3` changed one documented command string in `classroom.html` (`--tag 1.4.4` to `--tag 2.0.0`).

Both repeatable checks were rerun against HEAD `2c3c3f8e` plus the uncommitted Phase 10 closeout edits, none of which touch Phase 6 code:

| Check | Command | Result |
|-------|---------|--------|
| UI harness | `node scripts/check_classroom_ui.mjs` | `{"checks":115,"passed":true,"final":true}`, exit 0. The 5 extra checks are the 08.1 unslop guards. |
| Classroom Python tests | the same 11 test files as the original run, `-n 0 --basetemp=work/test-tmp-reverify6` | 214 passed, 1 skipped (the Windows-only path test) in 9.69s |

The browser behavior was rechecked in CI rather than locally: `Browser acceptance` run 45368870932 on `2f9521b2` succeeded on 2026-11-24T09:49:39Z. Since then the only classroom asset change is the command-string edit above, which changes no workspace behavior.

The earlier process notes about STATE.md being stale and the Phase 6 work being uncommitted are resolved: that work is committed and STATE.md is current. The status stays `human_needed` because the first-time learner walkthrough still needs a person.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | **SC1:** In every supported desktop lesson mode, the workspace identifies the current lesson, available actions, reading/runtime capability, readiness, and result location. | ✓ VERIFIED | `workspaceMode()` (classroom.js 1744 to 1844) is the single source for 7 kinds. `showCapability` renders `dl#workspace-mode` (Lesson type, Code runs in, Results appear in), the Run label, `#capability` readiness and Result visibility. Browser receipt `mode_samples` covers 8 sample keys across 7 lessons and 6 kinds (python, sql, worker ready, worker not ready, reading, draft, browser). Save-only and legacy reading are unit tested only, and they are absent from the published catalog: `curriculum/` registers only `python` (140) and `sql` (94) legacy runners. The `test_workspace_mode.py` fixtures pass. |
| 2 | **SC2:** Learners can operate the classroom with a keyboard and see clear focus and status cues; applicable contrast and accessibility checks pass. | ✓ VERIFIED | Receipt `keyboard`: all 9 steps true. `focus_walk`: 159 stops, `failures: []`. `axe`: version 4.14.1 with tags wcag2a, wcag2aa, wcag21a, wcag21aa and wcag22aa over 16 scans (8 pages x light/dark), with `blocking: []` and `recorded: []`, so 0 critical, serious, moderate or minor findings. `test_classroom_keyboard.py` checks accent contrast of at least 3:1 in both themes. Status regions use `role="status"` and `aria-live`. |
| 3 | **SC3:** Navigation, lesson switching, test setup, viewing old results, and runtime restart preserve drafts, progress, and receipts; viewing history never re-executes code. | ✓ VERIFIED | The receipt has 20 preservation entries with matching before and after hashes, covering: reload and lesson switch for legacy and module lessons, SQL reset (the test setup), opening an old run by keyboard, opening module history, and the browser copy conflict. The SQL reset uses `learner_snapshot`, which compares session, exerciseProgress, pad, padHistory and receipts. Module history uses `module_snapshot`, which compares session, exerciseProgress and history, plus `assert_no_execution_requests` and no save. The restart receipt has `verified: true` for bridge-01 and bayes-001. The node harness check "opening a module Saved runs entry sends no run or step request" passes. See the note below on restart progress and receipts. |
| 4 | Every lesson mode gets its labels, locations, ready copy and empty copy from one pure function, `workspaceMode(lesson, cap)`. | ✓ VERIFIED | The marked pure block exists once. `showCapability`, `resetResult` and `tryExample` call it. `test_workspace_mode.py` passes (12 fixtures plus 2 invariants). |
| 5 | Reading, draft and save-only lessons hide `#runtime-results` with the `hidden` attribute and never prompt a run. | ✓ VERIFIED | `$("runtime-results").hidden = !mode.showResults`. The browser gate asserts the `hidden` attribute is present, not CSS only, for apache-004 and dax-001. Harness check "reading lessons hide the Result panel and never prompt a run" passes. |
| 6 | Opening a finished module job shows the "Saved run from <time>" sentence, so an old run is not mistaken for the current one. | ✓ VERIFIED | `showJob` (classroom.js 3268 to 3274) uses the exact legacy sentence. The browser gate asserts `#run-storage-status` contains "Saved run" after the module history click. |
| 7 | A stale or unfingerprinted browser backup never silently replaces a newer server draft; the learner chooses and neither version is lost. | ✓ VERIFIED | `backupDecision` and `draftFingerprint` (classroom.js 1845 to 1882), the conflict store `ds60.classroom.conflict.<key>`, and `conflictPinned`, which blocks autosave from removing an unresolved backup. `test_draft_backup.py` passes. The harness checks "offered, not forced" (Use path) and "stale fingerprinted backup never overwrites" pass. The browser receipt check "A stale browser copy is offered, kept and discarded without replacing the draft" passes. |
| 8 | Clicking a Saved runs entry (legacy or module) never sends a run or step request. | ✓ VERIFIED | `renderHistory` click calls only `showJob`. The harness T1 check asserts no request at all, and the 06-02 mutation test proved it catches a regression. The browser `open_old_run` keyboard step and "Opening module history" both assert no execution actions and no save. |
| 9 | The palette opens with Cmd+K on macOS and Ctrl+K elsewhere, never inside the code editor. | ✓ VERIFIED | The `paletteShortcut` pure helper is wired at classroom-shell.js line 319. The vm tests pass, covering both platforms, Shift or Alt held, `.cm-editor` targets and targets without `closest`. The `isMac` regex matches "MacIntel" and not "Win32" or "Linux x86_64" (checked with node). In real Chromium on Linux, `palette_opens_lesson` and `palette_ignored_in_editor` are both true. |
| 10 | While the guided tour is open, the background is inert and Tab cannot leave the tour. | ✓ VERIFIED | `inertBackground` runs in startTour (classroom-guide.js line 844), and `restoreInert` is called in endTour before the layer is removed. The vm test covers apply and restore. Browser keyboard step `tour_traps_focus` is true. |
| 11 | The palette field and manual parts show a visible focus cue of at least 3:1, and a skip link jumps to the Result. | ✓ VERIFIED | `.palette-search:focus-within` and `.manual-parts li:focus` set an accent box-shadow. `#skip-result` is wired, and the browser step `skip_to_result` is true. `#run` has `aria-describedby="capability"`. |
| 12 | axe-core 4.14.1 finds no serious or critical violations in light and dark themes. | ✓ VERIFIED | Receipt `axe.version` is "4.14.1", with `blocking` and `recorded` both empty across 16 scans. The gate fails closed: it requires the exact version and `assert_axe_clean` raises on blocking findings. |
| 13 | The disposable stack is removed and no learner container or volume is touched. | ✓ VERIFIED | A read-only `docker ps -a` finds 0 `ds60-phase6*` containers and `docker volume ls` finds 0 such volumes. The 06-04 summary records protected containers and volumes as unchanged. |
| 14 | (Goal) First-time learners can operate the classroom **confidently**. | ? UNCERTAIN | This is a subjective outcome. Automated evidence proves the cues are present, correct and accessible, but not that learners feel confident. Routed to human verification (06-UAT.md item 1, D-04). |

**Score:** 13/14 truths verified (0 present but behavior unverified, 1 needs human judgment)

**Note on SC3 restart (Info, not a gap):** The browser restart stage checks only the draft source (`#source`) after `docker restart` of the lab container. Progress and receipts were not re-read in the browser after the restart. They are still covered for these reasons:
- `lab.py` (lines 90 to 97) derives the module state, `classroom-runs` and `progress.json` from the same directory as the drafts that survived the restart.
- `tests/test_classroom_runs.py::test_roundtrip_after_restart_preserves_exact_source_and_result` passes; it reopens the store and gets byte-identical receipts back.
- `tests/test_classroom_http.py` persists progress to disk.

Phase 7 SC2 qualifies restart and saved learner data in more depth.

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/ds60sqlpy/assets/classroom.js` | WORKSPACE MODE and DRAFT BACKUP pure blocks, renderWorkspaceMode, conflict panel, Saved run sentence | ✓ VERIFIED | Present, substantive and called from showCapability, resetResult, openLesson, queueSave and showJob. `git diff` adds 0 `innerHTML` lines. |
| `src/ds60sqlpy/assets/classroom.html` | `dl#workspace-mode`, `#skip-result`, `aria-describedby="capability"`, `tabindex="-1"` targets | ✓ VERIFIED | Lines 40, 181, 183, 563 and 658. |
| `src/ds60sqlpy/assets/classroom.css` | Workspace strip grid, palette and manual focus cues | ✓ VERIFIED | Lines 2919 and 3631, plus the `.workspace-mode` rules. |
| `src/ds60sqlpy/assets/classroom-shell.js` | SHELL KEY HELPERS, isMac, skip-result handler | ✓ VERIFIED | Lines 8 to 22, 319 and 338. |
| `src/ds60sqlpy/assets/classroom-guide.js` | TOUR INERT HELPER wired into start and end | ✓ VERIFIED | Lines 736 to 853. |
| `src/ds60sqlpy/assets/classroom-editor.js` | Orchestrator axe fixes (focusable scrollable code) | ✓ VERIFIED | Modified at 21:20, before the image build. Axe clean and focus walk clean. |
| `scripts/check_classroom_workspace.py` | Mode, keyboard, focus, axe, preservation and restart flows | ✓ VERIFIED | Wired from `check_classroom_browser.main` (lines 1036 to 1094). Ruff clean. |
| `tests/test_workspace_mode.py`, `tests/test_draft_backup.py`, `tests/test_classroom_keyboard.py` | Pure helper and static tests | ✓ VERIFIED | All pass. |
| `work/phase6-browser-receipts.json`, `work/phase6-restart-receipts.json` | Gate evidence | ✓ VERIFIED | `complete: true`, 27 checks, `restart.verified: true`. |
| `06-UAT.md` | human_needed record (D-04) | ✓ VERIFIED | 3 pending items, `blocking: false`. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `showCapability` | `workspaceMode(current, cap)` | single call | WIRED | Drives `#run`, `#runtime-results`, `#capability` and the strip. |
| `resetResult` | `workspaceMode` | emptyStatus and emptyOutput | WIRED | Copy outside the pure block names no Run button. |
| `openLesson` restore | `backupDecision` | restore, discard, conflict or none | WIRED | classroom.js line 1366. |
| `queueSave` success | `stashBases` | `draftFingerprint(fields)` | WIRED | classroom.js line 734, with the conflictPinned guard at line 743. |
| shell keydown | `paletteShortcut(event, isMac)` | condition | WIRED | classroom-shell.js line 319. |
| `startTour` / `endTour` | `inertBackground` / `restoreInert` | tour object | WIRED | classroom-guide.js lines 844, 853 and 750 to 752. |
| `check_classroom_browser.main` | `workspace_checks`, `restart_stage`, `assert_axe_clean` | import and call | WIRED | Lines 37 to 39 and 1062 to 1077. |
| `tests/test_module_ui.py` | `scripts/check_classroom_ui.mjs` | pinned receipt | WIRED | Pinned at 110 checks; the harness reports 110. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `#workspace-mode`, `#capability` | `mode`, `cap` | Server `capability` (`cap.ready`, `cap.detail`, `cap.profile`) from the module and legacy capability services | Yes. Real Chromium shows not-ready apache-001 with `cap.ready === false` and the exact not-ready sentence, and ready bayes-001 and bridge-01. | ✓ FLOWING |
| `#draft-conflict` | conflict list | localStorage `ds60.classroom.conflict.<key>` with server fields from `values()` | Yes, checked by the browser conflict check against the server-saved draft | ✓ FLOWING |
| `#run-storage-status` | `job.created_at` | Module job history from the server | Yes, checked in the browser after a real python-core run | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| UI harness (mode copy, backups, conflict, read-only history) | `node scripts/check_classroom_ui.mjs` | `{"checks":110,"passed":true,"final":true}`, 110 PASS lines, exit 0 | ✓ PASS |
| Classroom-related Python tests | `.venv/bin/python -m pytest -q -n 0 --basetemp=work/test-tmp-verify6` on test_workspace_mode, test_draft_backup, test_classroom_keyboard, test_module_ui, test_learning_editor, test_classroom_browser_probe, test_unified_classroom, test_classroom_http, test_web_development, test_module_drafts and test_classroom_runs | 214 passed, 1 skipped (a Windows-only path test) in 9.40s | ✓ PASS |
| Palette shortcut cases | `pytest ... tests/test_classroom_keyboard.py -k "shortcut or palette"` | 4 passed | ✓ PASS |
| Lint | `.venv/bin/ruff check src`, plus the Phase 6 scripts and tests | All checks passed | ✓ PASS |
| macOS detection | `node -e` with the shell's `isMac` regex | MacIntel true, Win32 false, Linux false | ✓ PASS |
| Real browser gate | not rerun (Docker forbidden); read `work/phase6-browser-receipts.json` | complete, 27 checks, axe 0 of every severity, keyboard 9/9, focus 159/0 failures | ✓ PASS (receipt) |

### Probe Execution

No `scripts/*/tests/probe-*.sh` exists, and no Phase 6 plan or summary declares one. Step 7c: not applicable.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| UX-01 | 06-01, 06-04 | Each desktop lesson mode identifies the lesson, actions, capability, readiness and result location | ✓ SATISFIED | Truths 1, 4, 5 and 6 |
| UX-02 | 06-03, 06-04 | Keyboard operation, focus and status cues, contrast and accessibility checks pass | ✓ SATISFIED | Truths 2 and 9 to 12 |
| STATE-01 | 06-02, 06-04 | Navigation, switching, old results, test setup and restart preserve drafts, progress and receipts; history never re-executes | ✓ SATISFIED | Truths 3, 7 and 8 |

No orphaned requirements: REQUIREMENTS.md maps only UX-01, UX-02 and STATE-01 to Phase 6, and all three are claimed by plans. The REQUIREMENTS.md traceability rows still read "Pending"; the orchestrator updates those.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| src/ds60sqlpy/assets/classroom.js | 4249 | "TODOs" in learner-facing copy ("Read its TODOs before running.") | ℹ️ Info | UI text about starter files, not a debt marker |
| scripts/check_classroom_workspace.py | n/a | `mode_sample_checks` records but does not assert the "Results appear in" cell (strip[5]) | ℹ️ Info | The recorded values match the expected copy, and the exact strings are asserted in `test_workspace_mode.py` |
| scripts/check_classroom_workspace.py | n/a | The `sql-snippet` and `sql-lesson` samples both use sql-01, so "8 lesson modes" covers 7 lessons | ℹ️ Info | The two pad modes are distinct; no kind is missing from the published catalog |

No TBD, FIXME or XXX markers appear in any Phase 6 file. No U+2013 or U+2014 appears in the six classroom assets or in `check_classroom_workspace.py`.

### Human Verification Required

#### 1. First-time learner confidence walkthrough

**Test:** Use a fresh desktop browser profile and a person new to the classroom. Without coaching, they open home, pick a first lesson, find where to type, run it and read the result. Then they open a reading lesson and explain the workspace strip.
**Expected:** They find the editor, Run and Result without help, they correctly say that a reading lesson runs no code and has no Result panel, and they report being able to continue on their own.
**Why human:** "Confidently" in the phase goal is a subjective learner outcome that no automated check can settle.

Two more pending items in `06-UAT.md` are not required for this verdict, because automated evidence already settles the success criteria they relate to. They may still be run as extra assurance:
- **Item 2, screen reader spot check.** `aria-describedby="capability"` and `role="group"` with `aria-labelledby` are present, axe reports 0 findings, and the gate asserts the `#capability` text.
- **Item 3, real-Mac Cmd+K.** The `paletteShortcut` vm cases pass for `mac=true`, the `isMac` regex was checked, and the same listener works in real Chromium.

### Gaps Summary

There are no gaps. All three roadmap success criteria and every plan must-have are met in the codebase, and both repeatable automated checks were rerun by the verifier: the node harness at 110/110 and pytest at 214 passed. The browser gate receipt is consistent with the current assets and image build times. One goal-level item needs a person: whether first-time learners feel confident using the classroom.

---

_Verified: 2026-11-24T05:37:19Z_
_Verifier: the agent (gsd-verifier)_
