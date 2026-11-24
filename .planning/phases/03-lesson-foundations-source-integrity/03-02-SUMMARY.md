---
phase: 03-lesson-foundations-source-integrity
plan: 02
status: complete
requirements: [CURR-02, CURR-07]
key_files:
  - src/ds60sqlpy/catalog_builder.py
---

# Plan 03-02 summary

## What was done

- Added 31 observable outcomes to `LESSON_OUTCOMES` in
  `src/ds60sqlpy/catalog_builder.py`: python-lang-02..04, python-numpy-01..08,
  python-pandas-01..07, python-algo-01..07 (after python-60) and
  sql-deep-01..06 (after sql-60). Each is one sentence of 18 to 23 words that
  starts with a curated observable verb and names the lesson's techniques and
  evidence, written from each lesson's companion guide (objectives and
  exercise list) and learner source.
- The sql-01 and sql-58/59/60 replacements were already present in the
  working tree; they were kept and rechecked.
- `build_catalog()` assigns `LESSON_OUTCOMES[id]` before the extension
  `outcome` field and `_derived_outcome`, so the new strings win. These ids
  come from `curriculum/extensions/python-sql-deepening.json` and
  `python-modernization.json`, which in the working tree also carry
  (uncommitted, earlier) `outcome` fields for the same ids; those are now
  overridden and can be dropped later to keep a single source.

## Verification evidence

- Classifier: `outcome_issue()` imported from
  `scripts/build_coverage_matrix.py` (inline, no file written) returned None
  for all 35 strings (31 new plus sql-01, sql-58, sql-59, sql-60). In the
  freshly built catalog every lesson has an outcome (missing 0) and no
  outcome is weak (weak 0). The catalog outcome equals `LESSON_OUTCOMES` for
  all 35 ids.
- `perl -CSD -ne 'print if /[\x{2014}\x{2013}]/' src/ds60sqlpy/catalog_builder.py`:
  no output.
- `.venv/bin/ruff check src/ds60sqlpy/catalog_builder.py`: All checks passed.
- `.venv/bin/ruff format --check src/ds60sqlpy/catalog_builder.py`: already
  formatted.
- `.venv/bin/mypy src`: no issues in 62 source files.
- `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-0302
  tests/test_coverage_matrix.py tests/test_catalog.py`: 21 passed, 1 failed.
  The failure is `test_committed_matrix_and_report_are_current`: the committed
  `curriculum/coverage-matrix.json` is stale (schema_version differs from the
  builder's `SCHEMA_VERSION = 3` in the working tree), which predates this
  edit and is fixed only by regeneration.

## Remaining work (orchestrator's final `make generate` pass)

- Regenerate `curriculum/catalog.json` and the generated readers. Skipped
  here: `scripts/build_catalog.py` writes `curriculum/catalog.json`, outside
  the allowed scope, and `make generate` touches `courses/`.
- Run `scripts/build_coverage_matrix.py --write` and `--check`, then rerun
  the tests above.
- Lower `FOUNDATION_GAP_CEILING["missing-outcome"]` in
  `tests/test_coverage_matrix.py` from 31 to 0 (and weak-outcome to the new
  count, expected 0) once the regenerated matrix confirms it.
- Optionally remove the duplicate `outcome` fields from the two extension
  JSON files.

## Orchestrator reconciliation (2026-11-23)

- Single source restored: the 31 outcomes moved out of `LESSON_OUTCOMES` and
  into the `outcome` fields of `curriculum/extensions/python-sql-deepening.json`
  (18) and `curriculum/extensions/python-modernization.json` (13), formatted
  with the pinned Prettier. Keeping them in `LESSON_OUTCOMES` broke
  `build_catalog` in fixture catalogs that omit the extensions ("Title or
  outcome overrides name unknown lessons").
- The built catalog still yields the same 31 strings.
- `tests/test_canonical_python_generators.py`, `test_curriculum_extensions.py`,
  `test_curriculum_network_visualization.py`,
  `test_llm_foundations_expert_review.py`, `test_ml_module_lessons.py`,
  `test_reviewed_formula_semantics.py`, `test_worker_operations.py`,
  `test_catalog*.py`, `test_coverage_matrix.py`: 280 passed, 125 skipped,
  1 failed. The failure is the stale committed matrix, which the 03-04 gate
  regenerates.
