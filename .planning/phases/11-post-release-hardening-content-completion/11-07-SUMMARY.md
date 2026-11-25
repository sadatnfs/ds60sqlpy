---
phase: 11-post-release-hardening-content-completion
plan: 07
subsystem: content
status: complete
requirements: [HARD-02]
requirements-completed: [HARD-02]
tags: [content, lesson-prose, templated-words, sql-contracts, track-qualification]
requires: [11-01]
provides:
  - lesson-specific teaching prose in place of repeated scaffold paragraphs in 21 tracks
  - one STUDY-GUIDE.md per rewritten track that holds the shared operating guidance
  - a prose_words metric and a largest-templated-share line in the coverage matrix
  - a test that fails any lesson whose templated share is above 0.50
  - SQL exercise contracts that agree across learner file, companion guide and solution for all 60 days
affects: [11-08]
key-files:
  created:
    - "courses/*/STUDY-GUIDE.md (21 track study guides)"
    - "courses/{c,cpp,csharp,dax,docker,go,java,javascript-typescript,kubernetes,rust,swift}/authoring/*teaching*, guidance, labs, notes and practice sources"
    - .planning/phases/11-post-release-hardening-content-completion/11-07-SUMMARY.md
  modified:
    - scripts/build_coverage_matrix.py
    - curriculum/coverage-matrix.json
    - curriculum/track-qualification.json
    - "docs/{coverage-matrix,lesson-depth-report,track-qualification}.md"
    - courses/apache-data-platforms/authoring/build.py
    - "courses/apache-data-platforms/authoring/programs/apache-{057,081..088}.md"
    - "sql/postgres-60day (learner files, guides and solutions)"
    - "tests/{test_coverage_matrix,test_track_qualification,test_apache_data_platforms}.py and 10 track content tests"
    - "lesson-pages/ and reference-pages/ (regenerated)"
decisions:
  - Shared operating guidance (launcher, saving, hints, tutor, troubleshooting, official docs) lives once per track in STUDY-GUIDE.md, and lessons link to it instead of repeating it.
  - Every audited section heading and lesson fact was kept; only the repeated scaffold paragraphs were rewritten.
  - The 0.50 per-lesson limit is measured as templated_words over prose_words, where prose_words counts only the scored paragraphs the templated metric reads.
  - R8 baselines were lowered to each rewritten track's new total, so R8 now blocks regrowth from the new level.
  - Authoring fragments must link correctly from their own location. The apache builder relocates ../../STUDY-GUIDE.md links when it embeds programs one level shallower, as it already did for project links.
commits: [8c7a5f4a]
actuals:
  tasks: 3
  commits: 1
completed: 2026-11-25
---

# Phase 11 Plan 07: replace templated lesson prose Summary

Repeated scaffold paragraphs are gone from 21 tracks (HARD-02). Templated prose words fell
from 835,161 to 71,137, a 91.5 percent drop against a target of at least 50 percent. The
largest per-lesson templated share is 0.32 (`mle-011`), against a limit of 0.50; no lesson is
above 0.40. Commit 8c7a5f4a touched 5,223 files (82 added, 5,141 modified; 92,789 insertions
and 77,835 deletions). Most of the file count is regenerated reader pages
(2,231 under `reference-pages/courses`).

## Approach

1. **Tracer.** Shared operating text moved into one `STUDY-GUIDE.md` per track, and lessons
   link to it. The metric dropped on the first track before the approach was rolled out.
2. **Track rewrites.** Fifteen parallel agents rewrote the per-exercise scaffolds track by
   track. Each kept every audited heading and lesson fact and wrote prose that names the
   lesson's own data, functions and failure modes. Generated tracks changed their authoring
   sources (for example the new `courses/go/authoring/teaching_part1.py` to `part6.py`), and
   `make generate` rebuilt the outputs.
3. **Ceilings.** R8 baselines and the corpus ceiling were lowered to the new totals.

## Templated words by track

| Track | Before | After |
| --- | ---: | ---: |
| sql | 194,391 | 188 |
| cuda | 69,931 | 0 |
| javascript-typescript | 69,429 | 4,277 |
| go | 61,712 | 0 |
| python | 57,268 | 9,581 |
| java | 54,115 | 6,016 |
| kubernetes | 31,598 | 258 |
| rust | 27,935 | 71 |
| swift | 27,932 | 0 |
| csharp | 26,305 | 0 |
| dax | 26,172 | 1,657 |
| c | 24,148 | 468 |
| deep-learning-pytorch | 19,980 | 3,645 |
| web-development | 17,765 | 136 |
| deep-learning-tensorflow | 17,628 | 581 |
| docker | 15,734 | 0 |
| scala-spark | 13,549 | 183 |
| r | 11,266 | 99 |
| dbt | 10,128 | 0 |
| cpp | 8,105 | 0 |
| apache-data-platforms | 7,970 | 1,877 |
| 19 smaller tracks, unchanged | 42,100 | 42,100 |
| **All 1,838 lessons** | **835,161** | **71,137** |

The 19 unchanged tracks each held 5,332 words or fewer and no lesson in them is above the
share limit.

## SQL contracts

- Each of the 60 PostgreSQL days states its exercise contract in three places: the learner
  `.sql` comment, the companion guide and the solution. All three now agree for every day.
- The solution queries for days 34, 35, 39, 48, 49, 54 and 58 did not meet their own
  contracts and were fixed.
- The guide SQL checker reported 122 passed and 0 failed against a disposable database.

## Metric, ceilings and ledger

- `scripts/build_coverage_matrix.py` records `prose_words` per lesson, adds
  `templated_share()`, and prints the largest share in `docs/coverage-matrix.md`.
- `tests/test_coverage_matrix.py`: `TEMPLATED_WORDS_CEILING` went from 835280 to 71250, and
  the new `test_no_lesson_is_mostly_templated_prose` enforces `MAX_TEMPLATED_SHARE = 0.50`.
- `curriculum/track-qualification.json`: R8 `templated_baseline` was lowered for the 21
  rewritten tracks, and each `templated_baseline_source` says so.
  `docs/track-qualification.md` explains the change.

## Verification

- `build_coverage_matrix.py --check`, track qualification and `scripts/course.py validate`
  (26 passed, 0 failed) pass.
- `courses/apache-data-platforms/authoring/build.py --check`: 179 subject outputs match.
- Full test suite, run twice in a row: 6,268 passed, 520 skipped and 0 failed each time.
- Repository gates (`SKIP_FORMAT=1`, with format checked separately): every gate passed
  except `secrets`. Its one finding is the developer's gitignored local `.env`, which the
  scanner flags on purpose and CI never sees. A direct scan without `.env` found 0 findings in
  the tree and in Git history.
- ruff, ruff format, mypy (440 files) and the dash gate are clean.

## Deviations

- **Two tests depended on the old content.**
  - `test_every_developed_unit_has_exact_source_and_explicit_execution_boundary` compared
    `examples/<key>.md` with the raw authoring program. `build.py` now exposes
    `relocate_program()`, and the test compares against its output.
  - `test_gap_and_status_rules` produced an "exceeds the recorded baseline" error by setting
    go's baseline to 0. Go's total is now 0 as well, so the test now adds one templated word to
    a go lesson in a matrix copy instead.
- **Broken study-guide links in apache programs.** Nine apache program sources linked to
  `../STUDY-GUIDE.md`, which is correct only after embedding. The sources now use the path
  that is correct from their own location, and the builder relocates it.
- **Earlier summaries.** The 11-01 to 11-06 summaries were committed with this plan.

## Self-Check: PASSED

Tasks 1 to 3 map to 8c7a5f4a. HARD-02 is met with a 91.5 percent reduction and a 0.32
largest share.
