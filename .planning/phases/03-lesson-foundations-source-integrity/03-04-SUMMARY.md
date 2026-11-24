---
phase: 03-lesson-foundations-source-integrity
plan: 04
status: complete
requirements: [CURR-02, CURR-07]
---

# Plan 03-04 summary

All outputs were regenerated from source with `make generate` and the
coverage matrix `--write`. Every foundation gap is closed, so
`FOUNDATION_GAP_CEILING` is 0 for every code in
`tests/test_coverage_matrix.py`.

## Results (live matrix, 2026-11-23)

| Gap | Baseline (03-01) | Now |
| --- | ---: | ---: |
| missing-outcome | 31 | 0 |
| weak-outcome | 132 | 0 |
| unknown-prerequisite | 0 | 0 |
| few-terms | 971 | 0 |
| missing-path | 0 | 0 |

- 1838 lessons over 40 tracks, all `authored`; every row has an outcome,
  no `outcome_issue`, no unknown prerequisites and at least 3 key terms.
- Lesson IDs, prerequisites and authored-versus-planned status were
  unchanged by the rebuilds; `scripts/check_modules.py` and the matrix
  `--check` agree with `curriculum/catalog.json`.

## Fixes made while closing the gate

- `scripts/check_classroom_ui.mjs`: a local variable named `using` made
  the repository's tree-sitter JavaScript parser read `await using;` as an
  explicit resource-management declaration. Renamed to `choosing`.
- `tests/test_track_qualification.py`: the R8 assertion assumed the matrix
  lacked `templated_words`. It now checks the three real cases: a total
  under the baseline passes, a matrix without the metric reports the
  missing metric, and a total over the baseline is an error.
- `courses/nlp/guides/nlp-021.md` and `nlp-022.md` gained key terms and
  spacing fixes after their inline-format parity records were bound. The
  records were rebound with prose-only changes (code fences unchanged);
  `record_inline_format_parity.py --verify` passes for 275 guides.

## Verification

See `03-VERIFICATION.md`.
