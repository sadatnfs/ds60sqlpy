---
phase: 05-walkthroughs-track-qualification
plan: 05
subsystem: curriculum qualification
status: complete
requirements: [WALK-03, CURR-05, CURR-06]
requirements_completed: [WALK-03, CURR-05, CURR-06]
tags: [rubric, track-qualification, walkthroughs, ci-evidence]
requires: [05-01, 05-02, 05-03, 05-04, 07-04]
provides: [enforced 40-track threshold, CI-cited runtime evidence, track qualification docs]
affects: [docs/track-qualification.md, docs/coverage-matrix.md, docs/validation.md, docs/README.md]
key-files:
  created:
    - scripts/record_track_runtime_evidence.py
    - tests/test_record_track_runtime_evidence.py
    - tests/fixtures/gh_run_view/app_build_run.json
    - reference-pages/docs/track-qualification.md.html
    - reference-pages/docs/walkthroughs.md.html
  modified:
    - scripts/check_track_qualification.py
    - scripts/build_coverage_matrix.py
    - tests/test_track_qualification.py
    - curriculum/track-qualification.json
    - docs/track-qualification.md
    - docs/coverage-matrix.md
    - docs/validation.md
    - docs/README.md
decisions:
  - "R8 baseline is the per-track templated-word sum at b1847ca7 (stricter than the post-Phase-3 total the plan described)"
  - "R10 pass for ordinary-profile tracks requires a recorded app-build run whose groups all passed"
  - "Evidence recorder refuses runs whose commit does not match the working-tree walkthrough inputs"
commits: [7f50b9da, bca223a5, Phase 10 closeout commit]
actuals:
  tasks: 3
  commits: 3
completed: 2026-11-24
---

# Phase 5 Plan 05: Track qualification closure Summary

All 40 ledger records are recomputed from the coverage matrix and all 40
meet the threshold. R9 counts only validated walkthroughs, R8 checks each
track against a templated baseline tied to a cited commit, and R10 `pass`
on the 32 tracks with ordinary profiles cites app-build run 45399494825 at
`0770e8fd`, where all 19 ordinary CI groups passed. The threshold test is
enforced with no xfail, and the docs carry the final rules, evidence fields
and a per-track results table.

## Preconditions

- `03-VERIFICATION.md` and `04-VERIFICATION.md` exist, and the 05-01 to 05-04 summaries exist.
- `scripts/build_coverage_matrix.py --check` reports "Coverage matrix is current". All 1838 rows carry `metrics.templated_words`, and the matrix has 0 gap codes.

## What changed

### scripts/check_track_qualification.py
- **R9** uses `ds60sqlpy.walkthroughs.load_walkthroughs(root, ModuleCatalog(root), track)` through `validated_walkthroughs` (the catalog is cached). A `ValueError` or `OSError` counts as zero coverage. R9 `pass` on an invalid file fails with "pass needs a valid walkthrough file".
- **R8** `pass` needs three things: the matrix metric, a non-boolean integer `templated_baseline` of at least 0, a track total at or below that baseline, and a `templated_baseline_source` that cites a 40-hex commit. Only R8 may carry baseline fields.
- **Runtime evidence:** `runtime.evidence` is optional and may appear only when `walkthrough_outputs_checked` is true. When `walkthrough_outputs_checked` is true, the record must have:
  - `evidence.ci_run`: a string of digits
  - `evidence.commit`: 40 lowercase hex characters
  - `evidence.groups`: a sorted, unique list of known groups that includes the `ci_group` of every ordinary profile
  
  A track with no ordinary group cannot claim checked outputs.
- **R10** `pass` on a track with ordinary profiles requires `walkthrough_outputs_checked` true, which in turn requires valid evidence.
- New helpers: `required_ci_groups`, `evidence_errors` and `evidence_pending` (true when R10 awaiting evidence is the only reason a track is below threshold).
- `--check` also prints how many tracks meet the threshold and lists the tracks awaiting evidence. `--track` prints the evidence or which groups are pending.

### curriculum/track-qualification.json (all 40 records)
- **R1 to R7:** `pass` everywhere, because the matrix measures 0 rows. The 10 tracks with no practice lessons keep a justified R6 and R7 `na`, which the checker still accepts. No accepted gaps exist, so no lesson IDs are listed.
- **R8:** `pass` with `templated_baseline` equal to the per-track sum at commit `b1847ca7e6f36bc851f39daa8e98a96770d371dc`, the first commit with the metric (catalog total 835280). The source is cited in `templated_baseline_source`.
- **R9:**
  - python and bridge: `pass` (live Python tracer)
  - sql: `pass` (live SQL planner)
  - dax: `pass` (hand-derived adapter)
  - cuda, docker, kubernetes, spark-deployment: justified `na` (no ordinary-profile runnable lessons; no universal automatic tracer is claimed)
  - All 32 authored tracks: `pass`, with validated walkthroughs covering all 3 stages (96 walkthroughs in total)
- **R10:** `pass` on all 40. The 8 tracks with no ordinary profile pass without evidence. The 32 tracks with ordinary profiles were first recorded as justified `gap` in `7f50b9da`, then moved to `pass` in `bca223a5` when `scripts/record_track_runtime_evidence.py` recorded app-build run 45399494825 at `0770e8fd4c58030c20d8267ed3820eb630d1442f`, where every one of the 19 ordinary CI groups passed its `Docker classroom (<group>)` job and qualify step.
- **R11:** `not-assessed` with its justification on every track (D-04).

### tests/test_track_qualification.py
- New tests: `test_r9_counts_only_validated_walkthroughs`, `test_r8_baseline_rule`, `test_walkthrough_outputs_checked_requires_ci_evidence`, `test_r10_pass_requires_ci_evidence_for_ordinary_profiles` and `test_below_threshold_tracks_only_await_ci_evidence`.
- The R8 assertions in `test_gap_and_status_rules` are updated for the new rule.
- `test_every_track_meets_threshold` is a plain parametrized test over all 40 tracks. The computed xfail helper from `7f50b9da` was removed in the closeout once every track qualified, so `grep -c xfail` prints 0.
- `test_ordinary_profile_tracks_cite_ci_evidence` (closeout) asserts that every track with an ordinary profile records `walkthrough_outputs_checked` true and cites a run, a 40-hex commit and every one of its groups.

### scripts/record_track_runtime_evidence.py (new) and its test
- Runs `gh run view RUN --repo sadatnfs/ds60sqlpy --json headSha,conclusion,jobs,workflowName`. This call is read-only.
- Checks that the run comes from the workflow `Application builds` (app-build.yml) and that `headSha` is 40 hex characters.
- Finds one job per CI group, named `Docker classroom (<group>)`. A group counts as succeeded only when the job and its `Qualify complete references...` step (`scripts/ci_classroom.py qualify --group "$CI_GROUP"`) both concluded `success`. If a group's job ran more than once, every run must have succeeded.
- Refuses to proceed unless the run commit exists locally and the working tree matches it in `courses`, `scripts/check_module_references.py` and `src/ds60sqlpy/walkthroughs.py`. This ensures the evidence covers the walkthroughs being recorded. For example, a dry run against the older successful run 45313712049 (commit 13470273) was correctly rejected.
- For each track whose required groups all succeeded, it sets `runtime.evidence = {ci_run, commit, groups}`, sets `walkthrough_outputs_checked: true` and sets R10 to `pass`. Other tracks are reported as `SKIP` with the outcome for each group and are left unchanged.
- Before writing, it re-runs `evaluate_track` on every record. It writes JSON in the Prettier layout; a test confirms the output matches the current file byte for byte. `--dry-run` prints the plan and writes nothing.
- `tests/test_record_track_runtime_evidence.py` uses the fixture `tests/fixtures/gh_run_view/app_build_run.json`, with no network access. It covers:
  - group parsing for success, failure, skipped, a missing qualify step, a repeated job and an unknown group
  - rejection of other workflows and malformed commits
  - updates applied only to tracks whose groups all succeeded
  - a run where every group succeeds, which qualifies all 40 tracks
  - the output format, including line width
  - numeric run ID validation

## Per-track status (R1 to R11)

P pass, na justified not applicable, n-a not-assessed (justified). Generated from `curriculum/track-qualification.json` at closeout.

| Track | Rows | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R8 baseline | CI groups (run 45399494825) | Threshold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| advanced-spark-modeling | 38 | P | P | P | P | P | na | na | P | P | P | n-a | 2585 | scala-spark | met |
| apache-data-platforms | 88 | P | P | P | P | P | na | na | P | P | P | n-a | 7970 | data-platforms | met |
| applied-science | 24 | P | P | P | P | P | na | na | P | P | P | n-a | 1071 | python-core | met |
| bayesian-computing | 24 | P | P | P | P | P | na | na | P | P | P | n-a | 1389 | bayesian, python-core, stan | met |
| bridge | 13 | P | P | P | P | P | P | P | P | P | P | n-a | 3192 | none (no ordinary profile) | met |
| c | 42 | P | P | P | P | P | P | P | P | P | P | n-a | 24148 | c-go | met |
| cpp | 42 | P | P | P | P | P | P | P | P | P | P | n-a | 8105 | cpp | met |
| csharp | 48 | P | P | P | P | P | P | P | P | P | P | n-a | 26305 | csharp | met |
| cuda | 128 | P | P | P | P | P | P | P | P | na | P | n-a | 69931 | none (no ordinary profile) | met |
| custom-likelihood-pytorch | 20 | P | P | P | P | P | na | na | P | P | P | n-a | 1067 | pytorch | met |
| data-ml-engineering | 72 | P | P | P | P | P | na | na | P | P | P | n-a | 2560 | data-engineering, python-core, pytorch, scala-spark | met |
| data-visualization | 8 | P | P | P | P | P | P | P | P | P | P | n-a | 640 | python-core | met |
| dax | 60 | P | P | P | P | P | P | P | P | P | P | n-a | 26172 | none (no ordinary profile) | met |
| dbt | 26 | P | P | P | P | P | P | P | P | P | P | n-a | 10128 | data-engineering | met |
| deep-learning-pytorch | 36 | P | P | P | P | P | P | P | P | P | P | n-a | 19980 | pytorch | met |
| deep-learning-tensorflow | 36 | P | P | P | P | P | P | P | P | P | P | n-a | 17628 | python-core, tensorflow | met |
| docker | 42 | P | P | P | P | P | P | P | P | na | P | n-a | 15734 | none (no ordinary profile) | met |
| go | 48 | P | P | P | P | P | P | P | P | P | P | n-a | 61712 | c-go | met |
| java | 36 | P | P | P | P | P | P | P | P | P | P | n-a | 54115 | java | met |
| javascript-typescript | 66 | P | P | P | P | P | P | P | P | P | P | n-a | 69429 | javascript-typescript | met |
| jax | 34 | P | P | P | P | P | P | P | P | P | P | n-a | 5332 | jax | met |
| julia | 32 | P | P | P | P | P | P | P | P | P | P | n-a | 4663 | julia | met |
| kubernetes | 66 | P | P | P | P | P | P | P | P | na | P | n-a | 31598 | none (no ordinary profile) | met |
| llm-applied | 24 | P | P | P | P | P | P | P | P | P | P | n-a | 640 | python-core, pytorch | met |
| llm-evaluation | 24 | P | P | P | P | P | P | P | P | P | P | n-a | 177 | python-core, pytorch | met |
| llm-theory | 48 | P | P | P | P | P | P | P | P | P | P | n-a | 651 | python-core, pytorch | met |
| ml-engineering | 18 | P | P | P | P | P | P | P | P | P | P | n-a | 4301 | data-engineering | met |
| nlp | 24 | P | P | P | P | P | P | P | P | P | P | n-a | 2687 | python-core | met |
| polars | 18 | P | P | P | P | P | P | P | P | P | P | n-a | 3719 | data-engineering | met |
| python | 102 | P | P | P | P | P | P | P | P | P | P | n-a | 57268 | none (no ordinary profile) | met |
| python-web | 72 | P | P | P | P | P | na | na | P | P | P | n-a | 3838 | python-web | met |
| r | 60 | P | P | P | P | P | P | P | P | P | P | n-a | 11266 | r | met |
| rust | 48 | P | P | P | P | P | P | P | P | P | P | n-a | 27935 | data-platforms | met |
| scala-spark | 42 | P | P | P | P | P | P | P | P | P | P | n-a | 13549 | scala-spark | met |
| spark-deployment | 18 | P | P | P | P | P | na | na | P | na | P | n-a | 720 | none (no ordinary profile) | met |
| sql | 86 | P | P | P | P | P | P | P | P | P | P | n-a | 194391 | none (no ordinary profile) | met |
| statistics-ml | 69 | P | P | P | P | P | na | na | P | P | P | n-a | 2020 | bayesian, python-core | met |
| swift | 48 | P | P | P | P | P | P | P | P | P | P | n-a | 27932 | swift | met |
| tmb-modeling | 48 | P | P | P | P | P | na | na | P | P | P | n-a | 848 | r | met |
| web-development | 60 | P | P | P | P | P | P | P | P | P | P | n-a | 17765 | php | met |

- **Meet the threshold:** all 40.
- **R6 and R7 na:** 10 tutorial-only tracks. **R9 na:** cuda, docker, kubernetes, spark-deployment. **R11:** not-assessed on all 40 (no human reviewer, per D-04).
- **Accepted-gap lesson IDs:** none. The matrix measures 0 gap rows.

## Task 3: documentation (closeout)

- `docs/track-qualification.md`: final R8 baseline rule, plain threshold wording, the `walkthrough_outputs_checked` and `evidence` fields, a "Recording CI evidence" section and a "Current results" table of all 40 tracks generated from the ledger.
- `docs/coverage-matrix.md`: cross-link to track qualification (R1 to R8 read the matrix). The file is generated, so the link was added in `scripts/build_coverage_matrix.py` and the matrix regenerated.
- `docs/validation.md`: after the result labels, a link explaining that the runtime ledger names the narrowest label per profile and that walkthrough expected outputs are checked in the reference corpus.
- `docs/README.md`: index entries for `track-qualification.md` and `walkthroughs.md`.
- `reference-pages/docs/*.html` regenerated with `scripts/build_lesson_readers.py` (2 new pages, 3 updated).
- No document claims universal automatic tracing (D-11). American English, no em or en dashes (D-15).

## Deviations from Plan

1. **[Rule 3 / scope] Task 1 tracer: go was not in the first passing set.** The new R10 evidence rule meant go (ordinary `c-go` group) could not pass until CI evidence existed. The tracer path was proven on go for every other rule; go passed once run 45399494825 was recorded.
2. **[Discretion] Computed xfail marks, later removed.** `7f50b9da` applied the strict xfail only to tracks awaiting evidence. After all 40 qualified, the closeout removed the helper so the test is a plain parametrized test (`grep -c xfail` prints 0), and added `test_ordinary_profile_tracks_cite_ci_evidence`.
3. **[Rule 3] Source of the R8 baseline.** Phases 3 and 4 landed together in `b1847ca7`, so no commit holds post-Phase-3 per-track totals. The baseline is the per-track sum at `b1847ca7e6f36bc851f39daa8e98a96770d371dc` (catalog total 835280), which is stricter, and is cited in each record.
4. **[Rule 2] Commit check in the evidence helper.** The helper refuses to record a run whose commit does not match the working-tree walkthrough inputs (threat T-05-16); a dry run against older run 45313712049 was correctly rejected.
5. **R10 gap instead of an evidence-pending status** while evidence was outstanding, so `--check` stayed green and the threshold stayed honest.
6. **[Rule 3] `check_module_references.py --list-only` needs arguments.** The plan's verify line omits them; the script requires `--profiles` and `--report`. Run with all 25 ordinary profiles and `--report work/p10/module-refs-list.json`: "Selected 1356 executable module implementations; 96 carry walkthrough expected output; nothing executed."
7. **Evidence predates the 2.0.0 pin bumps.** Run 45399494825 is at `0770e8fd`. Later commits bumped image pins for 2.0.0, and the release App builds run (45460757410) skipped the per-group Docker classroom jobs because the commit carried a publish marker. The Publish run 45460757558 ran "Qualify all Core references" and "Qualify every selected reference, failure and lifecycle contract" on amd64 and arm64, all successful, which covers the same corpus on the published images. This caveat is documented in `docs/track-qualification.md`.

## Gate results (closeout, 2026-11-24)

- `build_coverage_matrix.py --check`: Coverage matrix is current.
- `check_track_qualification.py --check`: 40 track records are consistent; threshold met by 40 of 40 tracks.
- `check_walkthroughs.py --check`: 96 authored walkthroughs across 32 tracks.
- `check_module_references.py --list-only --profiles <25 ordinary> --report work/p10/module-refs-list.json`: 1356 implementations selected, 96 with walkthrough expected output, nothing executed.
- pytest (05-05 set plus ci_contract, targeted_images, course_guide, lesson_reader, published_links, repository_guidance, web_reference_navigation, classroom_http, unified_classroom): 346 passed. After the coverage-matrix link: `test_coverage_matrix.py`, `test_track_qualification.py`, `test_repository_guidance.py` 138 passed.
- `ruff check`: clean. `ruff format --check`: 354 files formatted. `mypy src`: no issues in 62 files.
- `node scripts/check_classroom_ui.mjs`: 115 checks passed.
- `build_lesson_readers.py --check`: current (201 lessons, 6587 references). `check_published_links.py`: 6790 pages, 0 failures. `check_repository_guidance.py`: 193 documents, 0 failures.
- `grep -c xfail tests/test_track_qualification.py`: 0. Dash scan of changed files: clean.

## Known Stubs

None.

## Self-Check: PASSED

- Created files exist; `7f50b9da` and `bca223a5` exist in history; ledger and docs agree (40 of 40).
