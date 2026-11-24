---
phase: 02-catalog-wide-coverage-matrix
type: verification
status: passed
requirements: [CURR-01]
---

# Phase 2 verification: catalog-wide coverage matrix

## Success criteria

| # | Criterion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Every current subject, track, lesson and sequence is accounted for in a maintained catalog-driven matrix. | PASS | `tests/test_coverage_matrix.py::test_every_cataloged_lesson_has_exactly_one_known_row` compares the rows with `curriculum/catalog.json` and every module manifest. 1838 rows over 40 tracks. CI step "Check catalog coverage matrix drift" and `make generate` keep it maintained. |
| 2 | Each entry distinguishes authored from planned and reading-only from runnable content, and records its source, profile, dependencies, artifacts and known gaps. | PASS | Row fields `status`, `execution`, `learning_mode`, `paths`, `runtime`, `dependencies`, `prerequisites`, `verification`, `artifacts`, `variants` and `gaps`. Totals: 1838 authored, 0 planned; 1478 runnable, 348 reading, 12 operations. |

## Commands

```bash
.venv/bin/python scripts/build_coverage_matrix.py --check
.venv/bin/python -m pytest -n 0 tests/test_coverage_matrix.py tests/test_lesson_depth_audit.py
./scripts/lint-repo
./scripts/format-repo --check --language python
node scripts/check_classroom_ui.mjs
```

All exited 0. Pytest: 25 passed.
