---
phase: 03-lesson-foundations-source-integrity
plan: 03
status: complete
requirements: [CURR-02, CURR-07]
---

# Plan 03-03 summary

Module tracks gained observable outcomes and lesson-specific key terms in
their authoring sources, track group by track group (groups A to N in the
plan). Each group rebuilt its track from source with lesson IDs,
prerequisites and authored-versus-planned status unchanged.

## Results (live matrix, 2026-11-23)

| Gap | Baseline (03-01) | Now |
| --- | ---: | ---: |
| few-terms | 971 | 0 |
| weak-outcome | 132 | 3 |
| missing-outcome | 31 | 31 |

- The 3 remaining `weak-outcome` rows (sql-58, sql-59, sql-60) are core SQL
  lessons whose outcomes live in `LESSON_OUTCOMES` in
  `src/ds60sqlpy/catalog_builder.py`. The new entries are in place; the gap
  clears when the catalog is regenerated in 03-04.
- The 31 `missing-outcome` rows are core Python and SQL lessons (numpy,
  pandas, algorithms, language, deep SQL), handled by plan 03-02.
- Every `## Key terms` section uses `- **Term:** definition` bullets seeded
  from the plan lesson's `concepts`; the matrix counts at least 3 per guide.

## Verification

- `build_coverage_matrix.py --track <track> --gaps weak-outcome,few-terms,missing-outcome`
  reports no lessons for every module track.
- Track builds were rerun from source; `scripts/check_modules.py` passes.
