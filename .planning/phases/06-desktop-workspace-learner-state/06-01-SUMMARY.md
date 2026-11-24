---
phase: 06-desktop-workspace-learner-state
plan: 01
subsystem: classroom-ui
status: complete
requirements: [UX-01]
tags: [workspace, copy, ux, harness]
requires: []
provides:
  - "workspaceMode(lesson, cap) pure descriptor (classroom.js, // BEGIN WORKSPACE MODE PURE HELPERS)"
  - "renderWorkspaceMode(mode) and dl#workspace-mode strip under #capability"
affects: [06-02, 06-03, 06-04]
tech-stack:
  added: []
  patterns: ["marked pure helper block evaluated alone in a Node vm by pytest"]
key-files:
  created:
    - tests/test_workspace_mode.py
  modified:
    - src/ds60sqlpy/assets/classroom.js
    - src/ds60sqlpy/assets/classroom.html
    - src/ds60sqlpy/assets/classroom.css
    - scripts/check_classroom_ui.mjs
    - tests/test_module_ui.py
decisions:
  - "Harness baseline was 100 (05-02 landed first), so the pinned receipt is 105, not the plan's 100."
  - "resetResult() with no current lesson uses neutral copy (No run yet for this lesson.) so no copy outside the pure block names a Run button."
  - "A finished non-solution module job now shows the Saved run sentence; the existing harness check that expected an empty #run-storage-status was updated to the exact new sentence (D-07)."
metrics:
  completed: 2026-11-23
actuals:
  tasks: 3
  commits: 0
  note: "Commits are made by the orchestrator per exec-rules; this executor made none."
---

# Phase 6 Plan 01: Workspace mode descriptor Summary

The pure function `workspaceMode(lesson, cap)` now decides, for all seven lesson kinds (draft, reading, save-only, browser, python, sql, worker), the label, Run label, where code runs, where results appear, readiness text and the empty-result copy. `showCapability`, `resetResult` and `tryExample` read their copy from it. A new `dl#workspace-mode` strip under `#capability` shows "Lesson type", "Code runs in" and "Results appear in". Finished module jobs now get the same "Saved run from <time>" sentence that legacy receipts use.

## What was done

**Task 1 (tracer, reading end to end).**
- Added `// BEGIN WORKSPACE MODE PURE HELPERS` / `// END ...` directly after the diagnostic block. It contains `GPU_PROFILES` and `workspaceMode()` and uses no DOM or other globals.
- Added `renderWorkspaceMode(mode)`, which builds 3 dt/dd pairs with `node()` (no innerHTML).
- `showCapability` sets `#runtime-results.hidden = !mode.showResults`.
- `resetResult` writes `mode.emptyStatus` and `mode.emptyOutput`.
- HTML: added `<dl id="workspace-mode" class="workspace-mode" aria-label="How this lesson works" hidden>`. The `#output` default is now "What your program prints, and any error messages, appear here."
- CSS: `.workspace-mode` grid using only existing tokens (`--fs-sm`, `--muted`), plus a `[hidden]` guard because the rule sets `display: grid`.
- The tracer gate re-ran the verify command and it passed (3 pytest, harness 100/100) before expanding.

**Task 2 (every mode, TDD).**
- RED: 12 parametrized fixtures plus 2 invariant tests (no "Press Run" and no results panel for reading, draft and save-only; no en or em dashes in any copy). Result: 11 failed, 5 passed.
- GREEN: filled in the draft, save-only, browser, python, sql and worker copy exactly as the plan specifies. Worker `runsIn` names the profile's container and appends "(uses your NVIDIA GPU)" for GPU profiles. Module worker `readyText` now includes `cap.detail` (G2).
- `showCapability`:
  - `reading`, `draft`, `browser` and `saveOnly` now come from `mode.kind`.
  - The not-ready `<code>` sentence is unchanged byte for byte and only fires when `!mode.ready` for the python, sql, worker or browser kinds.
  - Otherwise `#capability` shows `mode.readyText + activity`, and the `warn` class applies only in the not-ready branch.
  - `#run.hidden` is `runLabel === null`. Run text is "Running..." during a legacy run, otherwise `mode.runLabel`.
  - Save-only lessons disable Run and hide `#runtime-setup` (G4).
- `tryExample` names the lesson's own Run label (G3).
- `showJob`: a finished non-solution job shows "Saved run[ from <locale time>]. It keeps the code that produced it, so opening it later never changes your editor." (G5). Solution jobs keep SOLUTION_JOB_NOTE, and unfinished jobs keep the old logic.

**Task 3 (harness).** Added 5 checks before the final receipt:
- reading hides results
- browser empty copy
- module worker location and detail
- legacy save-only
- old module job Saved run

`tests/test_module_ui.py` now pins `{"checks": 105, ...}`.

## Verification (real output)

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-06-01 -q tests/test_workspace_mode.py tests/test_learning_editor.py` (Task 1 tracer) | 3 passed |
| same, `tests/test_workspace_mode.py` after writing fixtures (RED) | 11 failed, 5 passed |
| same after implementation (GREEN) | 16 passed |
| `node scripts/check_classroom_ui.mjs \| tail -1` | `{"checks":105,"passed":true,"final":true}` |
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-06-01 -q tests/test_workspace_mode.py tests/test_module_ui.py tests/test_learning_editor.py` | 18 passed |
| same plus `tests/test_unified_classroom.py tests/test_classroom_http.py` | 42 passed |
| `.venv/bin/ruff check tests/test_workspace_mode.py tests/test_module_ui.py` | All checks passed! |
| `.venv/bin/ruff format --check tests/test_workspace_mode.py tests/test_module_ui.py` | 2 files already formatted |
| `.venv/bin/mypy src` | Success: no issues found in 62 source files |
| dash scan (perl) on all 6 touched files | no output, exit 0 |
| `grep -c "// BEGIN WORKSPACE MODE PURE HELPERS" classroom.js` | 1 |
| `grep -c 'id="workspace-mode"' classroom.html` | 1 |
| `grep -c "Press Run code" classroom.html` | 0 |
| "Press Run code" count in classroom.js outside the pure block | 0 |
| `grep -c '"checks": 105' tests/test_module_ui.py` | 1 |
| new `innerHTML` lines in the classroom.js diff | 0 |

No real browser run was done here. Plan 06-04 owns the browser gate. `scripts/check_plotly_browser.py` (draft keeps `#run` and `#runtime-results` hidden) and `scripts/check_classroom_browser.py` (`to_contain_text("Saved run")`) are compatible with the new behavior by inspection.

## Deviations from Plan

1. **[Rule 3, concurrent baseline] Check count 105, not 100.** Plan 05-02 had already raised the harness to 100 and left `tests/test_module_ui.py` pinned at a stale 95. As Task 3 instructs, I added exactly 5 checks and pinned 105.
2. **[Rule 1, plan self-conflict] Neutral null-lesson copy in resetResult.** Task 1 step 4 said to keep the old two strings when `current` is null, but the Task 2 acceptance check requires 0 "Press Run code" outside the pure block. I chose neutral copy: "No run yet for this lesson." (which matches the HTML default) and the new `#output` default.
3. **[D-07] Existing check updated.** In "marking exercises solved updates the index...", the check that a learner job after a solution job leaves `#run-storage-status` empty now asserts the exact "Saved run. It keeps the code..." sentence. That is the G5 behavior, and the solution note is still replaced.
4. **CSS addition:** a `.workspace-mode[hidden] { display: none; }` guard, because the grid display would otherwise override the hidden attribute.

## Notes for 06-02 and 06-03

- Use `workspaceMode(current, current.capability)` for any new copy about running. Do not add new inline `runtime_profile === "reading"` or browser checks. The pure block must stay free of DOM and global references, because `tests/test_workspace_mode.py` evaluates it alone in a vm.
- `#workspace-mode` is rendered on every `showCapability` call, and its children are `[dt, dd, dt, dd, dt, dd]`. The harness indexes `children[1]` (label) and `children[2]`/`children[3]` (Code runs in). Reordering rows will break those checks.
- The harness count is now **105**, pinned in `tests/test_module_ui.py:33`. Each new check needs that pin bumped.
- The not-ready sentence (`The <code>id</code> runtime is not ready. ...`) is unchanged and only applies to the python, sql, worker and browser kinds.
- Finished module jobs now overwrite `#run-storage-status` with the Saved run sentence.
- The impeccable design hook flagged existing literal values at classroom.css lines 3701 to 4018 (0.75rem, #3d4fd6). This plan did not add them and left them unchanged.
- The D-08 check `git diff --stat` shows changes in `catalog_builder.py`, `build_coverage_matrix.py` and `test_coverage_matrix.py`. Those come from other agents' in-flight work, not this plan.

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: tests/test_workspace_mode.py
- FOUND: BEGIN/END WORKSPACE MODE PURE HELPERS markers, `id="workspace-mode"`
- Commits: none by design (orchestrator commits).
