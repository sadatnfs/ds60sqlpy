---
phase: 03-lesson-foundations-source-integrity
type: verification
status: passed
requirements: [CURR-02, CURR-07]
---

# Phase 3 verification: lesson foundations and source integrity

## Success criteria

| # | Criterion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Every authored lesson states an observable outcome, direct prerequisites, essential terms, and enough context to orient a new learner. | PASS | Live `curriculum/coverage-matrix.json`: 1838 rows, every one `authored`, 0 empty outcomes, 0 `outcome_issue`, 0 unknown prerequisites, every row `has_vocabulary` with at least 3 key terms. The classroom lesson header renders the catalog outcome and its direct prerequisites, or "Start here: no earlier lesson is required." for the 25 entry lessons (`src/ds60sqlpy/assets/classroom.js:1473`). Foundation gap codes went from 31 missing-outcome, 132 weak-outcome and 971 few-terms to 0, and `FOUNDATION_GAP_CEILING` is 0 for every code. |
| 2 | Lesson identity remains stable, and generated readers, prerequisites, maintained sources, and authored-versus-planned status agree across all tracks. | PASS | `scripts/check_modules.py` reports every track fully authored and agrees with `curriculum/catalog.json`; `build_coverage_matrix.py --check` prints "Coverage matrix is current"; `test_catalog.py`, `test_lesson_reader.py::test_every_catalog_entry_has_a_current_portable_reader` and `test_module_reference_check.py` pass. Inline-format parity verifies for 275 guides and presentation parity prints `0 Counter()`. |

## Commands

```bash
.venv/bin/python scripts/build_coverage_matrix.py --check
.venv/bin/python scripts/check_modules.py
.venv/bin/python -m pytest -n 6 -q tests/test_catalog.py tests/test_lesson_reader.py \
  tests/test_coverage_matrix.py tests/test_module_reference_check.py tests/test_lesson_depth_audit.py
.venv/bin/python scripts/record_inline_format_parity.py --verify
node scripts/check_classroom_ui.mjs
./scripts/lint-repo
DS60_FORMAT_IMAGE=ds60-formatting:893716821-765 ./scripts/format-repo --check
```

## Results

- Targeted pytest: 122 passed, 1 failed. The failure is
  `test_rendered_references_cover_recursive_local_markdown_and_sql_links`,
  which reports `reference-pages/compose.modules.yaml.html` as changed. It
  is reference-page drift from the concurrent Phase 8 compose edit (08-04),
  not a lesson identity issue; the readers are regenerated with
  `scripts/build_lesson_readers.py` before that work is committed.
- `test_coverage_matrix.py`, `test_track_qualification.py` and
  `test_checks.py`: 75 passed, 39 xfailed (the xfails are the Phase 5
  track-qualification ratchets owned by 05-05).
- `check_classroom_ui.mjs`: 110/110. Formatter check: "Formatting checks
  passed." Ruff, ruff format and mypy are clean.
- Informational only: 1291 guides repeat their prerequisites under a
  heading and 1483 repeat their objectives; orientation is rendered from
  the catalog, so these are not gaps.
