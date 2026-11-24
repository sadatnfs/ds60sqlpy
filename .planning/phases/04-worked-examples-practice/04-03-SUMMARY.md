---
phase: 04-worked-examples-practice
plan: 03
status: complete
requirements: [CURR-03, CURR-04]
---

# Plan 04-03 summary

`make generate` and the matrix `--check` agree with the sources. Every
practice gap is closed, so `PRACTICE_GAP_CEILING` is 0 for every code and
`TEMPLATED_WORDS_CEILING` is the measured total of 835280.

## Results (live matrix, 2026-11-23)

| Gap | Baseline (04-01) | Now |
| --- | ---: | ---: |
| thin-guide | 418 | 0 |
| few-examples | 352 | 0 |
| few-exercises | 0 | 0 |
| missing-solution | 0 | 0 |
| thin-solution | 698 | 0 |
| templated words | 970529 | 835280 |

- Minimums over 1838 lessons: guide 1050 words, 2 worked examples and
  3 key terms; over the 1365 practice lessons: 6 exercises and a
  700-word solution.
- The templated total fell by 135249 words (13.9%) and is now a ceiling:
  it can fall but not rise.

## Fixes made while closing the gate

- `courses/dax/authoring/part08.py`: dax-046's solution wrote
  `[NetRevenue](0.2)` as plain text, which Markdown reads as a link to a
  missing file. It is now code, and the track was rebuilt with
  `courses/dax/authoring/build.py`.

## Spot-check

See `04-VERIFICATION.md` for the per-track accuracy sample and the fixes it
led to.
