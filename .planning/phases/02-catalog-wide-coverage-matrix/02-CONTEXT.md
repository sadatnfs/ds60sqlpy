---
phase: 02-catalog-wide-coverage-matrix
requirements: [CURR-01]
mode: mvp
---

# Phase 2 context: catalog-wide coverage matrix

## Goal

Plan the content phases (3 to 5) against a maintained, honest inventory of the
whole catalog instead of a showcase sample.

## Decisions

- The matrix is generated, never hand-edited. `scripts/build_coverage_matrix.py`
  reads `curriculum/catalog.json` and every module manifest through the same
  loaders the classroom uses, so the matrix cannot list a lesson the app does
  not ship.
- One row per core lesson and per canonical module lesson. Language variants
  (for example `cuda-001@cpu-model`) fold into their canonical row under
  `variants`, so a track is not double counted.
- Gaps reuse the thresholds in `scripts/audit_lesson_depth.py` (1050 guide
  words, 2 examples, 3 terms, 700 solution words, 6 exercises). Practice-only
  gaps are not raised for tutorial or reading lessons.
- Gaps are a work queue, not a failure. CI fails only on drift or on a
  cataloged lesson whose files are missing, which keeps the gate honest
  without blocking unrelated work.
- Instructional labels such as **Expected**, **Verify** and **Hint** are not
  counted as vocabulary terms, so the `few-terms` count reflects real
  definitions.

## Out of scope

Fixing the gaps themselves. Phases 3 to 5 consume the matrix.
