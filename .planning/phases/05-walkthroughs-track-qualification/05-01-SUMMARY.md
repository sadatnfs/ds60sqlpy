---
phase: 05-walkthroughs-track-qualification
plan: 01
subsystem: curriculum-qualification
status: complete
tags: [rubric, track-qualification, runtime-ledger, CURR-05, CURR-06]
requirements: [CURR-05, CURR-06]
requires: [curriculum/coverage-matrix.json, scripts/check_module_references.py, scripts/ci_profiles.py]
provides: [curriculum/track-qualification.json, scripts/check_track_qualification.py, rubric R1 to R11]
affects: [05-02, 05-03, 05-04, 05-05]
files_created:
  - curriculum/track-qualification.json
  - scripts/check_track_qualification.py
  - tests/test_track_qualification.py
  - docs/track-qualification.md
files_modified: []
scratch: [work/05-01/seed.py, work/05-01/doc.md]
completed: 2026-11-23
actuals:
  tasks: 3
  commits: 0
  tokens: 12000
---

# Phase 5 Plan 01: Track qualification contract Summary

I built a shared rubric (R1 to R11) and a curated ledger holding honest seed statuses
and a registry-derived runtime capability ledger for all 40 tracks. A read-only checker
recomputes every measured value from the coverage matrix. The per-track threshold test
is a strict xfail until 05-05.

## What was built

- `scripts/check_track_qualification.py` (stdlib plus existing repo modules, read-only):
  `load_matrix`, `load_ledger`, `measured_rows`, `expected_route`,
  `expected_walkthrough_route`, `ordinary_stages`, `walkthrough_stages` (plain JSON read
  of `courses/<track>/walkthroughs.json`), `evaluate_track`, `meets_threshold`,
  `report`, `check`. CLI: `--track T` and `--check`. Neither mode writes files.
- `curriculum/track-qualification.json`: `schema_version` 1, `rubric_version` 1, 40
  records. Each record has `track`, `family`, `rows`, `runtime` (profiles with derived
  route, narrowest label and CI group; unavailable profiles with the reasons from
  `EXTERNAL_REASONS`, copied exactly; `guide_examples`; `walkthrough_outputs_checked: false`),
  `walkthrough` (route, plus `floor` 3 for authored tracks, no stored count), all
  eleven criteria and `reviewed`. The layout matches Prettier.
- `tests/test_track_qualification.py`: 91 passing tests plus 40 strict xfails
  (`test_every_track_meets_threshold`, one per track).
- `docs/track-qualification.md`: rubric table, statuses, threshold and 10 percent cap,
  R11 honesty rule, runtime routes and labels, walkthrough routes, the statements that
  guide code blocks are not executed in this phase and that no universal automatic
  tracer exists, how to run the checker, and ledger authority (D-05).

## Seed statuses (provisional, measured from the matrix as committed on 2026-11-23)

| Criterion | pass | gap | na | not-assessed |
| --------- | ---- | --- | -- | ------------ |
| R1 | 40 | 0 | 0 | 0 |
| R2 | 33 | 7 (apache-data-platforms, cuda, llm-applied, llm-theory, python, sql, statistics-ml) | 0 | 0 |
| R3 | 15 | 25 | 0 | 0 |
| R4 | 30 | 10 | 0 | 0 |
| R5 | 25 | 15 | 0 | 0 |
| R6 | 30 | 0 | 10 (all-tutorial tracks) | 0 |
| R7 | 10 | 20 | 10 (all-tutorial tracks) | 0 |
| R8 | 0 | 40 (templated_words metric absent) | 0 | 0 |
| R9 | 4 (python, sql, bridge, dax) | 32 (authored tracks) | 4 (cuda, docker, kubernetes, spark-deployment) | 0 |
| R10 | 40 | 0 | 0 | 0 |
| R11 | 0 | 0 | 0 | 40 |

No `accepted-gap` was recorded. Every gap is open work, and none is presented as accepted.
Gap justifications name the gap codes and the owning phase but no counts or lesson lists,
so they do not go stale while Phases 3 and 4 shrink the queue. No track meets its
threshold yet, as expected.

## Verification (commands actually run)

- `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-05-01 tests/test_track_qualification.py -q` (Task 1 tracer, go only): 3 passed.
- `.venv/bin/python scripts/check_track_qualification.py --track go`: exit 0. Report showed R7 gap with 17 measured rows, R8 gap, R9 gap, consistency ok, threshold below (3 reasons). Ledger bytes unchanged (also asserted in a test).
- `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-05-01 tests/test_track_qualification.py tests/test_module_reference_check.py -q`: 91 passed, 40 xfailed.
- `.venv/bin/python scripts/check_track_qualification.py --check`: `OK 40 track records are consistent.`
- `-rxX` run: all 40 `test_every_track_meets_threshold[...]` are XFAIL (strict), with no XPASS.
- `.venv/bin/ruff check` and `ruff format --check` on the new script and test: clean.
- Prettier (`ds60-formatting` local image, `--network=none`, read-only mount) `--check` on the ledger and the doc: clean after the doc tables were formatted.
- Dash scan from the plan on all four files: `[]`, exit 0.
- `git status --short` on `scripts/build_coverage_matrix.py tests/test_coverage_matrix.py src/ds60sqlpy/catalog_builder.py curriculum/coverage-matrix.json`: the first three show `M` from Phase 3 and 4 agents. This plan did not edit them, and the matrix itself is unmodified.

Repo-wide gate results, all caused by other agents' in-flight files, none by this plan:
- `ruff check src scripts tests`: 6 errors in `scripts/verify_image_revision.py`, `tests/test_classroom_lifecycle.py` and `tests/test_image_revision.py`.
- `ruff format --check src scripts tests`: 4 files would be reformatted, none of them this plan's.
- `mypy src`: 1 error in `src/ds60sqlpy/walkthroughs.py:191` (05-02, in progress).

## Deviations from Plan

1. [Rule 2, correctness] Rules stricter than the plan text, to guard T-05-01 and T-05-02.
   `na` is rejected on any measured criterion that still has measured rows. It is allowed
   only on R4 (all-reading tracks), R6 and R7 (all-tutorial tracks) and R9 (no ordinary
   runnable lessons). `accepted-gap` is allowed only on R1 to R7. Each profile's `label`
   must equal the narrowest label for its route, not just any of the five labels. R9 must
   be `pass` for existing live and hand-derived adapters. `walkthrough.route` is derived
   from the matrix (core sql to live-sql, other core to live-python, dax-offline to
   hand-derived, no ordinary rows to na, else authored) and is not just recorded. R8
   `pass` needs the `templated_words` metric and a `templated_baseline` (forward
   compatible with 05-05).
2. `guide_examples` must start with one of three registered statements: core course
   checks, the CI reference corpus, or no ordinary executable reference. The plan gave a
   single fixed sentence, but that sentence would be false for core and reading-only
   tracks. Track notes are appended for cpp, javascript-typescript and statistics-ml.
3. The tests use `--basetemp=work/test-tmp-05-01` instead of `work/test-tmp`, per the
   orchestrator rules.
4. I made no commits and did not update STATE, ROADMAP or REQUIREMENTS, per the
   orchestrator rules, which override the executor's per-task commit protocol. STATE.md
   still lists Phase 3 as the focus, but this wave 1 plan has no dependencies and was
   dispatched by the orchestrator.

## Open items for 05-05 (must recompute)

- After Phases 3 and 4 regenerate `curriculum/coverage-matrix.json`, run `--check`.
  A recorded `pass` fails if new gap rows appear. `gap` stays consistent when rows
  shrink, so flip it to `pass`, or to `accepted-gap` with exact IDs within the 10 percent
  cap. R1, R2 and R10 must reach `pass`.
- R8: once the matrix carries `templated_words`, record a `templated_baseline` per track
  and flip it to `pass` where the total is at or below the baseline.
- R9: 05-02 has already created `courses/go/walkthroughs.json` covering the beginner,
  intermediate and advanced stages (plain JSON read), but go R9 stays `gap` until those
  entries are validated. Switch `walkthrough_stages` to validated entries from
  `ds60sqlpy.walkthroughs` and set `walkthrough_outputs_checked` once the CI corpus
  asserts expected outputs.
- R11: all 40 tracks are `not-assessed`; `pass` needs a named reviewer and a date.
- Remove the `xfail(strict=True)` marker from `test_every_track_meets_threshold`.
- Add the cross-links to `docs/track-qualification.md`; this plan added none.

## Self-Check: PASSED

All four files exist, `--check` exits 0, and the tests pass as listed above. No commits
were expected (the orchestrator commits).
