---
phase: 03-lesson-foundations-source-integrity
plan: 01
status: complete
requirements: [CURR-02, CURR-07]
---

# Plan 03-01 summary

- `scripts/build_coverage_matrix.py` now records `outcome_issue` per lesson
  and reports `weak-outcome` (lead word must be a curated observable verb,
  capitalized, sentence of at least 4 words). Schema version 2.
- `guide-no-orientation` is retired: the classroom header renders outcome and
  direct prerequisites from the catalog for every lesson.
- New read-only `--track TRACK [--gaps CODES]` listing for per-track work.
- `tests/test_coverage_matrix.py` ratchet: missing-outcome 31, weak-outcome
  132, few-terms 971; ceilings may only fall.
- Docs: outcome and key-term rules in `docs/content-authoring.md` and
  `docs/implementation/ADDING_A_MODULE.md`.

Baseline gaps: few-terms 971, thin-solution 698, thin-guide 418,
few-examples 352, weak-outcome 132, missing-outcome 31; 534 clean rows.
