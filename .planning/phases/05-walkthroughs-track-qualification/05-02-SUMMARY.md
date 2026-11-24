---
phase: 05-walkthroughs-track-qualification
plan: 02
subsystem: classroom-walkthroughs
status: complete
tags: [walkthroughs, module-tracks, ci, classroom-ui]
requirements: [WALK-03, CURR-05]
requires: [module catalog, module_service, classroom-guide.js step panel, check_module_references corpus]
provides: [courses/<track>/walkthroughs.json format, module-walkthrough action, authored step renderer, check_walkthroughs gate, walkthrough expected_output in reference corpus]
affects: [05-03, 05-04, Phase 6 classroom UI]
key-files:
  created:
    - src/ds60sqlpy/walkthroughs.py
    - scripts/check_walkthroughs.py
    - tests/test_walkthroughs.py
    - courses/go/walkthroughs.json
    - docs/walkthroughs.md
  modified:
    - src/ds60sqlpy/module_service.py
    - src/ds60sqlpy/assets/classroom-guide.js
    - src/ds60sqlpy/assets/classroom.html
    - src/ds60sqlpy/assets/classroom.css
    - scripts/check_module_references.py
    - scripts/check_classroom_ui.mjs
    - tests/test_module_api.py
    - tests/test_module_reference_check.py
    - .github/workflows/ci.yml
decisions:
  - Authored walkthroughs are hash-bound to the executable reference and labelled "Authored steps, not a live trace"; they never claim execution.
  - The module-walkthrough action requires reveal true and is read only.
  - One invalid entry fails the whole track closed (no walkthrough offered for that track) and CI --check catches it.
  - expected_output lines are asserted against the real reference run in check_module_references.
actuals:
  tasks: 3
  commits: 0 (orchestrator commits)
---

# Phase 5 Plan 2: Authored Walkthroughs Summary

Hash-bound, reveal-gated authored walkthroughs for module tracks, with a step-panel renderer
labelled "Authored steps, not a live trace", a CI gate with rebind, expected output checked
by the reference corpus, and Go at one walkthrough per stage (go-001, go-025, go-037).

## What was built

- `src/ds60sqlpy/walkthroughs.py`: validator, loader and payload builder. Rejects unknown
  keys, wrong evidence, non-ordinary profiles, wrong source paths, stale hashes, excerpt
  drift, backward steps, length overruns and em or en dashes in authored text.
- `module_service.py`: `module-walkthrough` action (refuses without `reveal: true` using
  REVEAL_MESSAGE) and `walkthrough_available` on `module-lesson`.
- Classroom: `#walk-reference` button and `#step-badge`; `startAuthored` drops stale
  responses by ticket, lesson and intent version, and errors say "Your code was not
  changed."; `renderAuthored` highlights the step range with a "What to notice" section.
  Core Python and SQL keep the live step-through unchanged.
- `scripts/check_walkthroughs.py`: `--check`, `--track T`, `--track T --rebind`.
- `check_module_references.py`: carries `expected_output` per case and fails with
  "{id} walkthrough expected output not observed: {text}".
- CI step "Validate authored walkthrough bindings".
- `docs/walkthroughs.md`: authoring guide.

## Verification (real results)

| Command | Result |
| --- | --- |
| `pytest -n 0 tests/test_walkthroughs.py test_module_api test_module_drafts test_module_reference_check test_execution test_declared_outputs test_scientific_artifacts` | 224 passed, 18 skipped (DB URL not set) |
| `pytest -n 0 tests/test_ci_classroom.py test_ci_contract test_ci_release_status test_docker_release test_docker_registry test_image_publication` | 143 passed |
| `node scripts/check_classroom_ui.mjs` | 100 checks, passed true (5 new authored tests) |
| `scripts/check_walkthroughs.py --check` | OK: 3 authored walkthroughs across 1 tracks; nothing executed. |
| `scripts/check_walkthroughs.py --track go` | beginner, intermediate, advanced covered; stages without one [] |
| `check_module_references.py --profiles go --list-only` | 48 cases; 3 carry walkthrough expected output |
| Go references in a disposable golang container, network none | go-001, go-025, go-037 print "All lesson checks passed.", exit 0 |
| `ruff check src scripts tests`, `ruff format --check` on changed files | clean |
| `mypy src scripts/check_walkthroughs.py` | no issues in 63 files |
| Dash scan on all changed files | none |

## Authoring format for 05-03 and 05-04

Edit only `courses/<track>/walkthroughs.json`. See `docs/walkthroughs.md` for full detail.

- Top level: `schema_version` 1, `track_id` equal to the directory, `evidence` "authored",
  `walkthroughs` list. No other keys.
- Entry keys only: `lesson_id`, `title` (max 200), `anchor` "reference", `source_path`
  (tutorial source, or the single non-Markdown practice solution), `source_sha256`
  (lowercase SHA-256 of current bytes), `expected_output` (1 to 5 strings, max 200 each,
  must appear in the real reference output), `steps` (3 to 20).
- Step keys only: `lines` [start, end] within the file with non-decreasing starts,
  `excerpt` exactly the lines joined with "\n", `title` (200), `explanation` (1200),
  `observe` (600).
- Ordinary runtime profiles only; at least one walkthrough per stage; no em or en dashes.
- Run `check_walkthroughs.py --check` and `--track T`; use `--rebind` only when excerpts
  still match.

## Deviations from Plan

1. **[Rule 3] `api()` instead of `lab()`** in classroom-guide.js: `/api/modules` requires
   the `module-` prefix and is the existing module channel.
2. **[Rule 3] Harness shims** in check_classroom_ui.mjs: Element `prepend()`, document
   `contains()`, and an `HTMLElement` stub, needed by the authored renderer tests.
3. **[Rule 1] Rebind by position**: a test showed value-based hash substitution rewrites
   the wrong entry when two entries share identical source bytes. Fixed to substitute
   positionally and refuse if the hash count does not match the entry count.
4. **Whole-track fail closed** when one entry is invalid (deliberate; CI catches it).
5. **Go verification** used a local golang container because Go is not installed on the
   host; CI runs the same references in the reference corpus.
6. **Pre-existing CSS design-hook findings** (0.75rem, #3d4fd6) left alone; new rules use
   existing tokens.
7. Real Chromium check of the authored panel is pending CI; the jsdom-style harness passes.

## Known Stubs

None.

## Self-Check: PASSED

All created files exist; all verification commands above were run in this session.
