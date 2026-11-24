---
phase: 05-walkthroughs-track-qualification
plan: 05
status: partial
subsystem: curriculum qualification
tags: [rubric, track-qualification, walkthroughs, ci-evidence]
requirements: [WALK-03, CURR-05, CURR-06]
requirements_completed: []
completed_tasks: [1, 2-local]
pending:
  - "Task 2: record real app-build CI runtime evidence (helper ready, run not yet available)"
  - "Task 3: docs, 05-VERIFICATION.md, REQUIREMENTS.md"
key-files:
  created:
    - scripts/record_track_runtime_evidence.py
    - tests/test_record_track_runtime_evidence.py
    - tests/fixtures/gh_run_view/app_build_run.json
  modified:
    - scripts/check_track_qualification.py
    - tests/test_track_qualification.py
    - curriculum/track-qualification.json
commits: 0
note: "Changes left uncommitted in the working tree by instruction (a concurrent executor owns Docker and workflow files)."
---

# Phase 5 Plan 05: Track qualification closure (partial) Summary

All 40 ledger records are recomputed from the current coverage matrix. R9 now
counts only validated walkthroughs, R8 checks each track against a templated
baseline tied to a specific commit, and R10 `pass` requires cited CI evidence
for tracks with ordinary profiles. 8 tracks meet the threshold now. The other
32 are blocked on one item only: R10 needs a recorded app-build run.

**Status: partial.** Task 1 and the local part of Task 2 are done. Recording
real CI evidence (Task 2) and all of Task 3 (docs, `05-VERIFICATION.md`,
REQUIREMENTS) are still pending. No requirement is marked complete. Nothing
is committed; every change is in the working tree.

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

### curriculum/track-qualification.json (all 40 records, reviewed 2026-11-23)
- **R1 to R7:** `pass` everywhere, because the matrix measures 0 rows. The 10 tracks with no practice lessons keep a justified R6 and R7 `na`, which the checker still accepts. No accepted gaps exist, so no lesson IDs are listed.
- **R8:** `pass` with `templated_baseline` equal to the per-track sum at commit `b1847ca7e6f36bc851f39daa8e98a96770d371dc`, the first commit with the metric (catalog total 835280). The source is cited in `templated_baseline_source`.
- **R9:**
  - python and bridge: `pass` (live Python tracer)
  - sql: `pass` (live SQL planner)
  - dax: `pass` (hand-derived adapter)
  - cuda, docker, kubernetes, spark-deployment: justified `na` (no ordinary-profile runnable lessons; no universal automatic tracer is claimed)
  - All 32 authored tracks: `pass`, with validated walkthroughs covering all 3 stages (96 walkthroughs in total)
- **R10:** `pass` for the 8 tracks with no ordinary profile. The 32 tracks with ordinary profiles record `gap`, with a justification that names their CI groups and the helper script.
- **R11:** `not-assessed` with its justification on every track (D-04).

### tests/test_track_qualification.py
- New tests: `test_r9_counts_only_validated_walkthroughs`, `test_r8_baseline_rule`, `test_walkthrough_outputs_checked_requires_ci_evidence`, `test_r10_pass_requires_ci_evidence_for_ordinary_profiles` and `test_below_threshold_tracks_only_await_ci_evidence`.
- The R8 assertions in `test_gap_and_status_rules` are updated for the new rule.
- `test_every_track_meets_threshold` takes its marks from the checker (see Deviations).

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

P pass, na justified not applicable, gap open gap, n-a not-assessed (justified).

| Track | Rows | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R8 baseline | Threshold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| advanced-spark-modeling | 38 | P | P | P | P | P | na | na | P | P | gap | n-a | 2585 | awaits CI evidence (scala-spark) |
| apache-data-platforms | 88 | P | P | P | P | P | na | na | P | P | gap | n-a | 7970 | awaits CI evidence (data-platforms) |
| applied-science | 24 | P | P | P | P | P | na | na | P | P | gap | n-a | 1071 | awaits CI evidence (python-core) |
| bayesian-computing | 24 | P | P | P | P | P | na | na | P | P | gap | n-a | 1389 | awaits CI evidence (bayesian, python-core, stan) |
| bridge | 13 | P | P | P | P | P | P | P | P | P | P | n-a | 3192 | met |
| c | 42 | P | P | P | P | P | P | P | P | P | gap | n-a | 24148 | awaits CI evidence (c-go) |
| cpp | 42 | P | P | P | P | P | P | P | P | P | gap | n-a | 8105 | awaits CI evidence (cpp) |
| csharp | 48 | P | P | P | P | P | P | P | P | P | gap | n-a | 26305 | awaits CI evidence (csharp) |
| cuda | 128 | P | P | P | P | P | P | P | P | na | P | n-a | 69931 | met |
| custom-likelihood-pytorch | 20 | P | P | P | P | P | na | na | P | P | gap | n-a | 1067 | awaits CI evidence (pytorch) |
| data-ml-engineering | 72 | P | P | P | P | P | na | na | P | P | gap | n-a | 2560 | awaits CI evidence (data-engineering, python-core, pytorch, scala-spark) |
| data-visualization | 8 | P | P | P | P | P | P | P | P | P | gap | n-a | 640 | awaits CI evidence (python-core) |
| dax | 60 | P | P | P | P | P | P | P | P | P | P | n-a | 26172 | met |
| dbt | 26 | P | P | P | P | P | P | P | P | P | gap | n-a | 10128 | awaits CI evidence (data-engineering) |
| deep-learning-pytorch | 36 | P | P | P | P | P | P | P | P | P | gap | n-a | 19980 | awaits CI evidence (pytorch) |
| deep-learning-tensorflow | 36 | P | P | P | P | P | P | P | P | P | gap | n-a | 17628 | awaits CI evidence (python-core, tensorflow) |
| docker | 42 | P | P | P | P | P | P | P | P | na | P | n-a | 15734 | met |
| go | 48 | P | P | P | P | P | P | P | P | P | gap | n-a | 61712 | awaits CI evidence (c-go) |
| java | 36 | P | P | P | P | P | P | P | P | P | gap | n-a | 54234 | awaits CI evidence (java) |
| javascript-typescript | 66 | P | P | P | P | P | P | P | P | P | gap | n-a | 69429 | awaits CI evidence (javascript-typescript) |
| jax | 34 | P | P | P | P | P | P | P | P | P | gap | n-a | 5332 | awaits CI evidence (jax) |
| julia | 32 | P | P | P | P | P | P | P | P | P | gap | n-a | 4663 | awaits CI evidence (julia) |
| kubernetes | 66 | P | P | P | P | P | P | P | P | na | P | n-a | 31598 | met |
| llm-applied | 24 | P | P | P | P | P | P | P | P | P | gap | n-a | 640 | awaits CI evidence (python-core, pytorch) |
| llm-evaluation | 24 | P | P | P | P | P | P | P | P | P | gap | n-a | 177 | awaits CI evidence (python-core, pytorch) |
| llm-theory | 48 | P | P | P | P | P | P | P | P | P | gap | n-a | 651 | awaits CI evidence (python-core, pytorch) |
| ml-engineering | 18 | P | P | P | P | P | P | P | P | P | gap | n-a | 4301 | awaits CI evidence (data-engineering) |
| nlp | 24 | P | P | P | P | P | P | P | P | P | gap | n-a | 2687 | awaits CI evidence (python-core) |
| polars | 18 | P | P | P | P | P | P | P | P | P | gap | n-a | 3719 | awaits CI evidence (data-engineering) |
| python | 102 | P | P | P | P | P | P | P | P | P | P | n-a | 57268 | met |
| python-web | 72 | P | P | P | P | P | na | na | P | P | gap | n-a | 3838 | awaits CI evidence (python-web) |
| r | 60 | P | P | P | P | P | P | P | P | P | gap | n-a | 11266 | awaits CI evidence (r) |
| rust | 48 | P | P | P | P | P | P | P | P | P | gap | n-a | 27935 | awaits CI evidence (data-platforms) |
| scala-spark | 42 | P | P | P | P | P | P | P | P | P | gap | n-a | 13549 | awaits CI evidence (scala-spark) |
| spark-deployment | 18 | P | P | P | P | P | na | na | P | na | P | n-a | 720 | met |
| sql | 86 | P | P | P | P | P | P | P | P | P | P | n-a | 194391 | met |
| statistics-ml | 69 | P | P | P | P | P | na | na | P | P | gap | n-a | 2020 | awaits CI evidence (bayesian, python-core) |
| swift | 48 | P | P | P | P | P | P | P | P | P | gap | n-a | 27932 | awaits CI evidence (swift) |
| tmb-modeling | 48 | P | P | P | P | P | na | na | P | P | gap | n-a | 848 | awaits CI evidence (r) |
| web-development | 60 | P | P | P | P | P | P | P | P | P | gap | n-a | 17765 | awaits CI evidence (php) |

- **Meet the threshold now (8):** bridge, cuda, dax, docker, kubernetes, python, spark-deployment, sql.
- **Await CI evidence (32):** every other track. In each case R10 is the only reason, which `test_below_threshold_tracks_only_await_ci_evidence` enforces. Together these tracks need all 19 ordinary CI groups.
- **Accepted-gap lesson IDs:** none. The matrix measures 0 gap rows, so no criterion uses `accepted-gap`.

## Orchestrator: recording CI evidence

After the local commits are pushed and an app-build run on that commit finishes with every `Docker classroom (<group>)` job passing:

```bash
gh run list --repo sadatnfs/ds60sqlpy --workflow app-build.yml --limit 5 --json databaseId,headSha,conclusion,status
.venv/bin/python scripts/record_track_runtime_evidence.py --run RUN_ID --dry-run
.venv/bin/python scripts/record_track_runtime_evidence.py --run RUN_ID
.venv/bin/python scripts/check_track_qualification.py --check
.venv/bin/python -m pytest -n 0 -q -p no:cacheprovider --basetemp=work/test-tmp-0505 tests/test_track_qualification.py tests/test_record_track_runtime_evidence.py -rxX
```

The run commit must be fetched locally, and the working tree must match it under `courses`, `scripts/check_module_references.py` and `src/ds60sqlpy/walkthroughs.py`. Once the ledger is written, the computed xfail marks disappear on their own; the tests should then report 0 xfailed.

## Deviations from Plan

1. **[Rule 3 / scope] Task 1 tracer: go is not in the passing set.** The plan set `FINAL = {"go"}`. However, the new R10 evidence rule (required by Task 2 and the orchestrator instructions) means go, which uses the ordinary `c-go` group, cannot pass R10 until CI evidence is recorded. The tracer path is still proven on go: every rule except R10 passes (validated R9 on 3 stages, R8 within its baseline), and `--track go` shows R10 as the only remaining reason.
2. **[Discretion] Threshold marks are computed, not hard-coded.** `test_every_track_meets_threshold` builds each parameter with `_threshold_param`, which adds the strict xfail mark only when `evidence_pending` is true. As a result, the literal `xfail` appears once in the file (`grep -c xfail` prints 1, not 0), but no mark is applied once all 40 tracks qualify. A track below threshold for any other reason fails, both here and in `test_below_threshold_tracks_only_await_ci_evidence`. Task 3 may remove the branch after evidence is recorded if the literal zero count is required.
3. **[Rule 3] Source of the R8 baseline.** Phase 4 recorded only catalog totals: 970529 after Phase 3 and 835280 after Phase 4. No commit holds per-track totals from after Phase 3, because Phases 3 and 4 landed together in `b1847ca7`. The per-track baseline is therefore the sum at `b1847ca7e6f36bc851f39daa8e98a96770d371dc` (catalog total 835280). This baseline is stricter than the one the plan described, and it is cited in each record.
4. **[Rule 2] Commit check in the helper.** The helper refuses to record evidence unless the run commit matches the working-tree walkthrough inputs. Without this check, an older green run could be credited to walkthroughs it never executed (threat T-05-16).
5. **R10 gap instead of an evidence-pending status.** The plan already says that tracks missing CI evidence stay below threshold. Recording R10 as a justified `gap` keeps `--check` green (the records are consistent) while the threshold stays honest, so no new status was added.

## Gate results (local)

- `build_coverage_matrix.py --check`: Coverage matrix is current.
- `check_walkthroughs.py --check`: OK, 96 authored walkthroughs across 32 tracks; nothing executed.
- `check_track_qualification.py --check`: OK, 40 track records are consistent. 8 of 40 meet the threshold; 32 await CI evidence (R10).
- pytest on `test_track_qualification.py`, `test_record_track_runtime_evidence.py`, `test_walkthroughs.py` and `test_module_reference_check.py`: 155 passed, 32 xfailed (computed strict marks for the evidence-pending tracks), 0 xpassed.
- `ruff format --check scripts tests src`: clean.
- `mypy src`: no issues in 62 files.
- `ruff check scripts tests src`: 1 error, outside this plan's scope. It is E501 in `tests/test_classroom_launchers.py:105`, a file the concurrent 08-04 executor is editing; it was not touched here. Every file changed by this plan passes ruff.
- `docs/implementation/runtime-reference-evidence.json`, `scripts/build_coverage_matrix.py`, `tests/test_coverage_matrix.py` and `src/ds60sqlpy/catalog_builder.py` are unchanged.
- Dash scan over every file this plan created or changed: no em or en dashes.

## Known Stubs

None. R10 `gap` on 32 tracks is a recorded, justified pending item, not a stub.

## Self-Check: PASSED

- Created files exist: `scripts/record_track_runtime_evidence.py`, `tests/test_record_track_runtime_evidence.py`, `tests/fixtures/gh_run_view/app_build_run.json`.
- No commits are claimed (by instruction, everything is uncommitted).
