---
phase: 02-catalog-wide-coverage-matrix
plan: 01
status: complete
requirements: [CURR-01]
key-files:
  created:
    - scripts/build_coverage_matrix.py
    - curriculum/coverage-matrix.json
    - docs/coverage-matrix.md
    - tests/test_coverage_matrix.py
  modified:
    - Makefile
    - .github/workflows/ci.yml
    - docs/README.md
    - docs/content-authoring.md
    - docs/curriculum-gap-backlog.md
    - docs/implementation/ADDING_A_MODULE.md
---

# Plan 02-01 summary: catalog coverage matrix

## What shipped

- A generator that turns both catalogs into one row per lesson: 1838 rows
  (201 core, 1637 canonical module lessons) across 40 tracks, with 236
  language variants folded into 173 canonical rows.
- Each row records family, track, sequence, level, status (authored or
  planned), learning mode (practice or tutorial), execution (runnable,
  reading or operations), runtime profile, language, network,
  dependencies, prerequisites, outcome, source paths, verification kind,
  expected artifacts, variants, depth metrics and gap codes.
- `make generate` writes the matrix; CI fails when it drifts or when a
  cataloged lesson loses a file.

## Baseline for Phases 3 to 5

| Gap | Lessons |
| --- | ---: |
| few-terms | 971 |
| thin-solution | 698 |
| thin-guide | 418 |
| few-examples | 352 |
| guide-no-orientation | 332 |
| missing-outcome | 31 (all core) |
| missing-path, unknown-prerequisite, few-exercises, missing-solution | 0 |

565 lessons have no recorded gap. Core Python, SQL and bridge lessons only
lack catalog outcomes.

## Deviations

- The first `term_count` counted instructional labels (Expected, Verify,
  Hint) as terms, which hid real vocabulary gaps. It now skips them and
  counts standalone bold concept lines and bold terms inside vocabulary
  sections.
- All 1838 rows are authored; the catalog has no planned lessons today.
  The `status` field and the totals line keep the distinction visible for
  future planned entries.

## Verification

- `build_coverage_matrix.py --check`: current.
- `pytest tests/test_coverage_matrix.py tests/test_lesson_depth_audit.py`:
  25 passed.
- ruff, mypy, `./scripts/lint-repo`, `./scripts/format-repo --check
  --language python` and `node scripts/check_classroom_ui.mjs` (95 checks)
  pass.
