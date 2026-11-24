---
phase: 04-worked-examples-practice
plan: 01
status: complete
requirements: [CURR-03, CURR-04]
---

# Plan 04-01 summary

- `scripts/build_coverage_matrix.py` records `templated_words` per lesson.
  Guide and Markdown solution prose is split into paragraphs (fenced code,
  headings and tables removed); paragraphs of at least
  `TEMPLATE_MIN_WORDS = 20` words are sampled as 8-word shingles, and a
  paragraph counts as templated when at least half of its sampled shingles
  occur in `TEMPLATE_LESSONS = 3` or more lessons.
- The read-only `--track` helper prints the track's templated-word total.
- `tests/test_coverage_matrix.py` adds `PRACTICE_GAP_CEILING`
  (thin-guide 418, few-examples 352, thin-solution 698) and
  `TEMPLATED_WORDS_CEILING = 970529`, plus detector tests
  (`test_prose_paragraphs_skip_code_headings_and_short_text`,
  `test_templated_word_counts_need_three_lessons`).
- `docs/content-authoring.md` documents the worked-example rule (at least
  two focused, interpreted examples per guide) and solution reasoning rules.

## Verification

- `build_coverage_matrix.py --check`, `pytest tests/test_coverage_matrix.py`,
  ruff, format and mypy passed at the time of the plan.
