# Phase 5 context: walkthroughs and track qualification

**Gathered:** 2026-11-23 (autopilot; the project owner approved the v1
requirements and the recommendations in `05-RESEARCH.md`)
**Status:** Ready for planning

## Requirements

- WALK-03: each existing track that benefits from a guided worked-example or
  solution walkthrough provides a course-appropriate explanation through a
  tested adapter or authored steps, without claiming universal automatic
  tracing.
- CURR-05: each runnable example is checked against its registered runtime and
  required data or fixture, with actual behavior matching the explanation;
  unsupported or unavailable capabilities are identified honestly.
- CURR-06: every existing language and subject track is reviewed against the
  shared quality rubric and reaches its acceptance threshold, with each
  non-applicable criterion or remaining gap explicitly justified.

## Findings (from 05-RESEARCH.md, rechecked 2026-11-23)

- Live walkthroughs exist only for the core catalog: the Python line tracer
  and SQL clause planner in `src/ds60sqlpy/step_through.py`, gated by
  `lab.py:364-371` and `classroom-guide.js:54-58` (`stepLanguage`). Module
  lessons route to `ModuleService.action` (`module_service.py:233`), which has
  no walkthrough action and ends with "Unknown module action." (`:390`).
- The only authored-steps precedent is DAX: `module_drafts.worked_examples`
  (`module_drafts.py:61`) binds hand-derived traces by SHA-256
  (`_hashed_file`, `:51`) and returns `"executed": False`.
- The CI reference corpus already runs the exact executable reference chosen
  by `scripts/check_module_references.py::reference_case` (`:91`) and checks
  it in `verify_result` (`:173`). `ORDINARY_PROFILES` (`:34`) and
  `EXTERNAL_REASONS` (`:41`) already name every excluded profile with a
  reason. `scripts/ci_profiles.py::groups` (`:25`) maps every ordinary
  profile to exactly one CI group.
- `curriculum/coverage-matrix.json` (schema 2, 1838 rows, 40 tracks, families
  `core` and `module`) is the measured gap source. Gap codes:
  missing-path, missing-outcome, unknown-prerequisite, weak-outcome,
  thin-guide, few-examples, few-terms, few-exercises, missing-solution,
  thin-solution. The Phase 4 `templated_words` metric is not yet present.
- Every one of the 32 authored-walkthrough tracks has at least one
  ordinary-profile lesson in each of its three stages (beginner,
  intermediate, advanced), so every floor walkthrough can be anchored on a
  reference the CI corpus executes.
- No shared rubric exists anywhere in the repository.

## Decisions

- **D-01 Plan breakdown.** Five plans, as recommended by research:
  05-01 qualification contract (wave 1); 05-02 authored walkthrough format,
  adapter and the go track (wave 1); 05-03 walkthroughs for compiled, JVM,
  web, R and Julia tracks (wave 2); 05-04 walkthroughs for Python, data, ML
  and science tracks (wave 2); 05-05 closure (wave 3, after Phase 3 and
  Phase 4 verification).
- **D-02 Rubric.** Criteria R1 to R11, defined once in
  `docs/track-qualification.md` and recorded per track in
  `curriculum/track-qualification.json`:
  R1 structure and paths (missing-path, unknown-prerequisite);
  R2 observable outcome (missing-outcome, weak-outcome);
  R3 vocabulary (few-terms); R4 worked examples (few-examples);
  R5 guide depth (thin-guide); R6 practice ramp (few-exercises, practice
  lessons); R7 solution reasoning (missing-solution, thin-solution);
  R8 lesson-specific prose (Phase 4 `templated_words`);
  R9 walkthrough (live adapter, DAX adapter, or authored floor met);
  R10 runtime honesty (capability ledger complete and consistent);
  R11 human clarity review.
- **D-03 Threshold and accepted gaps.** A track meets its threshold when
  every criterion is `pass`, a justified `na`, or a justified `accepted-gap`
  (R11 may also be a justified `not-assessed`, see D-04). An `accepted-gap`
  lists the exact lesson IDs, the test recomputes them from the matrix and
  requires equality, and the list may hold at most 10 percent of the track's
  lessons (integer check: `len(lessons) * 10 <= track_rows`). R1, R2 and R10
  must be `pass` with no accepted gaps. Justifications are at least 40
  characters.
- **D-04 Human review.** R11 may be recorded as `not-assessed` with an honest
  justification; it is never recorded as `pass` without a named reviewer and
  date.
- **D-05 Ledger authority.** `curriculum/track-qualification.json` is the
  authoritative, curated (hand-edited, not generated) per-track ledger.
  `docs/implementation/runtime-reference-evidence.json` is left as is.
- **D-06 Threshold ratchet.** `test_every_track_meets_threshold` in
  `tests/test_track_qualification.py` is marked
  `pytest.mark.xfail(strict=True)` from 05-01 until 05-05 removes the marker
  after recomputing every rubric value.
- **D-07 Authored walkthrough format.** One file per track,
  `courses/<track>/walkthroughs.json`, `schema_version` 1, `evidence`
  exactly `"authored"`. Each entry binds to the lesson's executable reference
  (the path `reference_case` selects: tutorial `source_path`, practice single
  non-Markdown solution) by `source_sha256`, with 3 to 20 line-anchored steps
  whose `excerpt` must equal the file text at those lines. Validated by
  `src/ds60sqlpy/walkthroughs.py` and `scripts/check_walkthroughs.py
  --check`.
- **D-08 Server action.** `ModuleService.action` gains `module-walkthrough`,
  returning `kind: "authored"`, `label: "Authored steps, not a live trace"`,
  `evidence: "authored"`, `executed: false`. Solution-anchored walkthroughs
  require `reveal is True` and reuse `REVEAL_MESSAGE` (`exercises.py:37`).
  `module-lesson` gains `walkthrough_available`.
- **D-09 Renderer.** The existing `#step-panel` renders a third `authored`
  kind with the visible label "Authored steps, not a live trace". Module
  lessons never send `step-through`; `stepLanguage` is not extended.
- **D-10 Density.** One authored walkthrough per track stage is the floor
  (3 per authored track, 96 in total). More are allowed; the test enforces
  the floor, not a maximum.
- **D-11 Live tracing boundary.** Live tracing stays with the core python and
  sql tracks, and bridge (core Python lessons) uses the live Python tracer.
  dax keeps its existing hand-derived adapter. cuda, docker, kubernetes and
  spark-deployment record R9 as justified `na` (no ordinary-profile runnable
  lessons). No document, label or record claims universal automatic tracing.
- **D-12 Execution evidence.** Each walkthrough's `expected_output` strings
  are asserted against the real reference job output in
  `check_module_references.verify_result`, which runs in the CI profile
  groups. Guide code blocks are not newly executed in this phase; existing
  content rendering checks cover them, and each track's ledger states this.
- **D-13 First track.** go is the tracer track in 05-02 and reaches its
  3-walkthrough floor there.
- **D-14 Coordination.** 05-01 and 05-02 do not edit
  `src/ds60sqlpy/catalog_builder.py`, `scripts/build_coverage_matrix.py` or
  `tests/test_coverage_matrix.py` (owned by Phases 3 and 4). Wave 2 plans
  (05-03, 05-04) edit only `courses/<track>/walkthroughs.json` for their
  tracks and track-local docs. Nobody hand-edits
  `curriculum/coverage-matrix.json`.
- **D-15 Style.** No em dashes or en dashes in any file, string, JSON value,
  test or commit text. American English. Desktop only.
- **D-16 Verification commands.**
  `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp <files>`,
  `.venv/bin/ruff check src scripts tests`,
  `.venv/bin/ruff format --check src scripts tests`, `.venv/bin/mypy src`,
  `node scripts/check_classroom_ui.mjs`,
  `.venv/bin/python scripts/check_walkthroughs.py --check`,
  `.venv/bin/python scripts/check_module_references.py --list-only`.

## The agent's Discretion (choices recorded)

- Walkthrough anchors are limited to lessons whose runtime profile is in
  `ORDINARY_PROFILES`, so every `expected_output` is checked by the CI corpus
  (D-12). Every authored track has such a lesson in each stage.
- The reference selection rule moves into
  `walkthroughs.executable_reference_path(lesson)` and
  `check_module_references.reference_case` calls it, so the corpus and the
  walkthrough binding cannot disagree.
- R8 measures non-regression: a track passes when its `templated_words`
  total is at or below the `templated_baseline` recorded for it in the
  ledger at 05-05 from the Phase 4 post-Phase-3 baseline. While the matrix
  has no `templated_words` metric, R8 cannot be `pass` (the test enforces
  this) and is recorded as `gap`.
- R9 counting in 05-01 reads walkthrough files as plain JSON (so 05-01 does
  not depend on 05-02); 05-05 switches the count to validated entries from
  `ds60sqlpy.walkthroughs`.
- Runtime ledger `route` per profile is derived, not free text:
  core family `course-check`; ordinary `reference-corpus`;
  `BROWSER_PROFILES` `browser-workflow`; `k8s-kind` `kubernetes-workflow`;
  `dax-offline` `hand-derived`; `reading` `reading-only`; `GPU_PROFILES`
  `gpu-separate`. Labels use the narrowest of the five result labels in
  `docs/validation.md:558-561`.
- JSON files are hand-authored and must pass `./scripts/format-repo --check`
  (Prettier owns `.json`). `--rebind` edits only the hash string in place.

## Deferred Ideas (out of scope)

- A universal automatic tracer or new live tracers for other languages.
- Conceptual authored walkthroughs for reading or operations tracks (cuda,
  docker, kubernetes, spark-deployment).
- Executing guide code fences beyond existing checks.
- Adding ledger fields to `scripts/build_coverage_matrix.py`.
- Rewriting existing templated scaffolding (Phase 4 decision 6).
- Mobile layouts; adaptive sequencing; new subject families.
