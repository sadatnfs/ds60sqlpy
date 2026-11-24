---
phase: 06-desktop-workspace-learner-state
plan: 04
subsystem: classroom-browser-gate
status: complete
requirements: [UX-01, UX-02, STATE-01]
tags: [browser-gate, playwright, axe-core, keyboard, learner-state, qual-02]
requires: [06-01, 06-02, 06-03]
provides:
  - "scripts/check_classroom_workspace.py: Phase 6 browser flows (mode samples, keyboard, focus walk, axe, preservation, browser copy conflict, restart stages, authored walkthrough)"
  - "check_classroom_browser.py flags --axe-script, --restart-stage write|verify, --restart-marker and receipt keys mode_samples, keyboard, focus_walk, axe, restart, authored_walkthrough"
  - "Pinned axe-core 4.14.1 at ~/.cache/ds60sqlpy/axe with PROVENANCE.json, mounted read-only at /axe by run-browser.sh"
  - "06-UAT.md human_needed record (D-04)"
affects: [phase-6-verification]
tech-stack:
  added: ["axe-core 4.14.1 (outside the repo, injected at test time only)"]
  patterns:
    - "Workspace flows live in a separate module that imports the gate lazily (_gate()) to avoid a cycle"
    - "axe evidence is recorded first and asserted after the remaining checks (assert_axe_clean), so one run keeps all evidence"
key-files:
  created:
    - scripts/check_classroom_workspace.py
    - .planning/phases/06-desktop-workspace-learner-state/06-UAT.md
  modified:
    - scripts/check_classroom_browser.py
    - tests/test_classroom_browser_probe.py
    - ~/.cache/ds60sqlpy/run-browser.sh (outside the repo, /axe mount only)
decisions:
  - "Module lessons use module_snapshot / assert_module_state_unchanged (same key shape as learner_snapshot), because learner_snapshot reads the legacy lab pad and runner."
  - "axe runs with iframes false: saved plot and browser preview frames are separate documents without axe injected."
  - "Serious and critical axe findings stay blocking. The gate was never relaxed; the product findings were fixed in the assets by the orchestrator, then the gate passed with 0 findings."
  - "assert_axe_clean runs after fixture_checks, so the gate still fails on axe but the receipt also proves every other check."
  - "The authored walkthrough check uses go-001 (first id in courses/go/walkthroughs.json) and records stale_hidden: server-validated."
metrics:
  completed: 2026-11-24
  stage_b_start: 2026-11-24T04:59:41Z
  stage_b_end: 2026-11-24T05:13:18Z
  final_run_start: 2026-11-24T05:27:30Z
  final_run_end: 2026-11-24T05:35:00Z
actuals:
  tokens: 14000
  tasks: 3
  commits: 0
  plan_head_before: 5ad22de5443ca3567e221032de0580ee224f4621
  plan_head_after: 5ad22de5443ca3567e221032de0580ee224f4621
  note: "exec-rules forbid commits and index changes. The orchestrator commits. All changes are uncommitted in the shared tree by instruction."
---

# Phase 6 Plan 04: Desktop workspace browser gate Summary

Real Chromium on a disposable stack now proves the Phase 6 behavior, and the pinned axe-core 4.14.1 scan finds 0 serious or critical issues in both themes. That covers 8 workspace modes, a 9-step keyboard-only flow, 159 focus stops, the browser copy conflict panel, draft preservation, a classroom container restart and the go-001 authored walkthrough.

## Receipts (final run, image rebuilt from the tree with the orchestrator's accessibility fixes)

- Main gate: `work/phase6-browser-receipts.json`. It has schema_version 1, scope classroom-and-fixtures, `complete: true` and 27 passed checks. Log: `work/06-04/gate6.log`.
- Restart write: `work/phase6-restart-write.json` (complete).
- Restart verify: `work/phase6-restart-receipts.json` (`complete: true`, `restart.verified: true`).
- The restart marker was deleted after verify passed.
- Plan verify command: True.

### Key receipt values

| Key | Value |
| --- | --- |
| mode_samples (8) | legacy-python bridge-01, sql-snippet sql-01, sql-lesson sql-01, module-ready bayes-001, module-not-ready apache-001, module-reading apache-004, dax-offline dax-001, browser-preview js-043 |
| keyboard | all 9 steps true: skip_to_content, palette_opens_lesson, palette_ignored_in_editor, save_shortcut, leave_editor, run_shortcut, skip_to_result, open_old_run, tour_traps_focus (Saved runs reached within the 60-press limit) |
| focus_walk | 159 stops, failures [] |
| authored_walkthrough | track go, go-001, 5 steps, first step "Package and imports", keyboard_step true, requests ["walkthrough"] only, stale_hidden "server-validated" |
| restart | write, then `docker restart ds60-phase6-browser-lab-1` only (postgres and worker start times unchanged), then verify: bridge-01 and bayes-001 drafts intact, no conflict prompt, verified true |
| axe | version 4.14.1, 16 scans (home, 6 lesson modes and the open palette, each in light and dark) |

axe findings by impact:

| Theme | Critical | Serious | Moderate | Minor |
| --- | --- | --- | --- | --- |
| Light | 0 | 0 | 0 | 0 |
| Dark | 0 | 0 | 0 | 0 |

### History of the axe gap (resolved)

The first full run found 27 serious rule instances: label-content-name-mismatch 52 nodes per theme, scrollable-region-focusable 16 per theme, and color-contrast 2 in dark. Their causes were:

- subject card aria-labels
- the A−/A+ code size buttons
- scrollable code `pre` elements that were not keyboard focusable
- the dark theme selected thumb-tab

These were outside 06-04 files_modified, so they were recorded rather than fixed here. The orchestrator then fixed them in `src/ds60sqlpy/assets` (classroom.js, classroom.html, classroom.css, classroom-editor.js). The rebuilt image passed with 0 findings, and the keyboard and focus checks still pass with the newly focusable code blocks.

### Passed checks in the final run

All 16 existing gate checks and the fixture checks (js-029, js-030, js-031) passed (D-07). These Phase 6 checks also passed:

- the strip, Run label and Result panel match 8 lesson modes
- the go-001 authored walkthrough opens, steps and closes without a run
- a keyboard-only learner can skip, search, save, run, jump to results and review
- 159 focus stops show a visible cue
- a stale browser copy is offered, kept and discarded without replacing the draft
- drafts survive reload and lesson switches, and SQL reset and history never run or save
- axe-core 4.14.1 finds no serious or critical issues on 16 scans
- there are no uncaught exceptions, HTTP failures or external requests

## Deviations from Plan

### Auto-fixed issues (test-side assumptions only, the product was correct)

1. **[Rule 1] Reading focus hid the Result panel.** Tutorial lessons (bayes-001) open in reading focus by design, and the choice is kept per track. Added `show_practice` to `open_lesson` and `goto_lesson`.
2. **[Rule 1] Appended print never ran.** The bridge-01 starter ends with `raise SystemExit(main())`. The keyboard flow replaces the draft with Control+A, and the save and run shortcuts are still exercised.
3. **[Rule 1] Skip to result after reload.** Lesson load moves focus into the page, so the check focuses the first skip link and requires Skip to result as the very next Tab stop (limit 2).
4. **[Rule 2] axe evidence.** `classify_axe` records up to 5 `targets` per finding. `assert_axe_clean` (new, tested) runs after `fixture_checks`, so one run keeps all evidence and still fails on any blocking finding.
5. **[Rule 1] Restart verify started before the library loaded.** The just-restarted classroom was still showing "Loading the classroom library..." when the 5 second lesson wait expired. The verify stage now opens the home page first (90 second library wait) and then each lesson. The first verify attempt failed for this reason. Because the marker was removed after that failure, write, restart and verify were all rerun cleanly.

### Environment

- Stale TeX inputs blocked image builds twice. In stage B the orchestrator regenerated them. In the final run, under the orchestrator's standing instruction, this executor ran `.venv/bin/python scripts/compile_lesson_tex.py` (4341 expressions), which changed only the generated `curriculum/tex-inputs.json`, `src/ds60sqlpy/_tex_cache_digest.py` and `src/ds60sqlpy/assets/vendor/textbook/compiled-tex.json`. The retry built cleanly.
- `./classroom up --rebuild` refreshes the shared local tags `ds60sqlpy-lab:1.4.3` and `ds60sqlpy-worker-python-core:1.4.3`, and may refresh `postgres:17` (the old digest became `<none>`). No project-specific image was tagged, so none were removed.
- Repo-wide `ruff check` reports errors only under `courses/` (content agents' in-progress files). `ruff check scripts src tests` is clean. Out of scope.

## Verification

- `pytest -n 0 --basetemp=work/test-tmp-06-04 tests/test_classroom_browser_probe.py`: 33 passed (final). Plan set with test_module_ui, test_workspace_mode, test_draft_backup and test_classroom_keyboard: 69 passed in stage B. The basetemp was removed.
- `ruff check` and `ruff format --check` on the plan files are clean. `mypy src` and `mypy scripts/check_classroom_workspace.py` report no issues.
- The axe integrity is pinned and verified (npm pack and openssl). There is no `node_modules/axe-core` in the repo.
- Dash scan on all files touched: none.

## Teardown and protected resources (final run)

- `down -v` removed the stack containers, 3 volumes and 2 networks. `.classroom/ds60-phase6-browser` was removed. ds60-phase6-browser leftovers: 0 containers, 0 volumes, 0 networks.
- Protected containers (ds60-classroom*, awesome-copilot*, tender_feistel, condescending_kirch): 14 before, 14 after. Protected volumes: 3 before, 3 after. Volume diff: none.
- Container diff: only other agents' random-named containers (stoic_allen gone, upbeat_bardeen added).
- Image diff: another agent removed its `ds60-p8-scan/*` images and added `ds60-formatting-julia`. `postgres:<none>` and `mirror.gcr.io/library/postgres:<none>` swapped as described above. This executor removed no images.

## Human UAT

06-UAT.md, `status: human_needed`, non-blocking (D-04), with 3 pending checks: first-time clarity, a screen reader spot check, and macOS Cmd+K.

## Self-Check: PASSED

- FOUND: scripts/check_classroom_workspace.py, 06-UAT.md, work/phase6-browser-receipts.json, work/phase6-restart-receipts.json, ~/.cache/ds60sqlpy/axe/PROVENANCE.json
- Commits: none by instruction (exec-rules); plan_head_before equals plan_head_after.

