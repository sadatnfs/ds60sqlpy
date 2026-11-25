# Track qualification

Every language and subject track is reviewed against one shared rubric (CURR-06)
and carries an honest runtime capability ledger (CURR-05). The results live in
`curriculum/track-qualification.json`, which is curated by hand and is the
authoritative record. `docs/implementation/runtime-reference-evidence.json` is a
historical record of earlier local runs and is not consulted by these checks.

The ledger records judgments only. Every measured value is recomputed by
`scripts/check_track_qualification.py` from `curriculum/coverage-matrix.json`, the
runtime profile registry (`scripts/check_module_references.py`) and the CI profile
groups (`scripts/ci_profiles.py`), so a record cannot claim more than the sources
support.

## Rubric

| ID  | Criterion             | Measure                                                       | Pass rule                                                                         | `na` allowed                                                 |
| --- | --------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| R1  | Structure and paths   | Matrix rows with `missing-path` or `unknown-prerequisite`     | Zero rows                                                                         | No                                                           |
| R2  | Observable outcome    | Matrix rows with `missing-outcome` or `weak-outcome`          | Zero rows                                                                         | No                                                           |
| R3  | Vocabulary            | Matrix rows with `few-terms`                                  | Zero rows, or an accepted gap within the cap                                      | No                                                           |
| R4  | Worked examples       | Matrix rows with `few-examples`                               | Zero rows, or an accepted gap within the cap                                      | Only when every lesson is a reading lesson, with zero rows   |
| R5  | Guide depth           | Matrix rows with `thin-guide`                                 | Zero rows, or an accepted gap within the cap                                      | No                                                           |
| R6  | Practice ramp         | Matrix rows with `few-exercises` (practice lessons only)      | Zero rows, or an accepted gap within the cap                                      | Only when every lesson is a tutorial                         |
| R7  | Solution reasoning    | Matrix rows with `missing-solution` or `thin-solution`        | Zero rows, or an accepted gap within the cap                                      | Only when every lesson is a tutorial                         |
| R8  | Lesson-specific prose | Track total of the Phase 4 `templated_words` metric           | Total at or below the `templated_baseline` recorded for the track                 | No                                                           |
| R9  | Walkthrough           | Live adapter, DAX hand-derived adapter, or the authored floor | Adapter exists, or authored walkthroughs cover every stage with a runnable lesson | Only when the track has no ordinary-profile runnable lessons |
| R10 | Runtime honesty       | Runtime capability ledger below                               | Complete and consistent with the registry and CI groups                           | No                                                           |
| R11 | Human clarity review  | A named person reads the track for clarity                    | `pass` only with a named `reviewer` and an ISO `date`                             | No; record `not-assessed` honestly instead                   |

Thresholds behind the measured gap codes are the matrix thresholds documented in
`docs/coverage-matrix.md` (guide 1050 words, 2 examples, 3 terms, 6 exercises,
solution 700 words). R8 compares the track's current `templated_words` total
with its `templated_baseline`, the per-track sum at commit
`b1847ca7e6f36bc851f39daa8e98a96770d371dc` (the first commit carrying the
metric, catalog total 835280). Each record cites that source in
`templated_baseline_source`. Phase 11 (plan 11-07) rewrote repeated scaffold
paragraphs as lesson-specific teaching and lowered each affected baseline to its
new per-track total, so the catalog total fell from 835161 to 71137; the source
text of each lowered record says so. The baseline is a ceiling, not a target: R8
stops a track from adding boilerplate but does not prove the remaining templated
prose is gone.

## Statuses

- `pass`: the criterion is met. For R1 to R7 the matrix must measure zero rows.
- `na`: the criterion does not apply, only where the table allows it, never while
  the matrix measures rows for it, and always with a justification.
- `accepted-gap`: a known shortfall accepted for this track. Allowed only on R1 to
  R7. The record lists the exact lesson IDs; the check recomputes them from the
  matrix and requires the lists to be equal.
- `gap`: open work. It carries a justification and no lesson list, because the
  matrix itself is the open queue and a stored list would go stale while content
  changes. A `gap` stays consistent when the measured rows shrink; the closure
  plan recomputes it.
- `not-assessed`: allowed only on R11.

Every status other than `pass` needs a justification of at least 40 characters.
No string in the ledger may contain an em dash or an en dash.

## Threshold

A track meets its threshold when every criterion is `pass`, a justified `na`, or
a justified `accepted-gap` within the cap, and R11 may also be a justified
`not-assessed`. R1, R2 and R10 must be `pass`; they accept no gaps. The cap is
10 percent of the track's lessons, checked with integers:
`len(lessons) * 10 <= track_rows`. Accepted gaps always name exact lesson IDs.

`tests/test_track_qualification.py::test_every_track_meets_threshold` checks this
for each track as a plain test with no expected-failure marks. All 40 tracks meet
the threshold; a track that falls below it fails the test.

## Human review

R11 is never recorded as `pass` without a named reviewer and a date. Until a
person has read the track for clarity, the honest status is `not-assessed` with a
justification that says so.

## Runtime capability ledger

Each record has a `runtime` block:

- `profiles`: exactly the runtime profiles the matrix lists for the track. Each
  profile has a `route` derived from the registry and the narrowest result label
  that route can claim. Ordinary profiles also name their CI group.
- `unavailable`: every profile outside the ordinary worker set (except core
  lessons), with the reason registered in `EXTERNAL_REASONS`, word for word.
- `guide_examples`: what checks the guide code. `scripts/check_guide_examples.py`
  runs or statically checks every guide code block (see "Guide example execution"
  in `docs/validation.md`); it reports documentation blocks, blocks marked
  `fragment` or `external`, and GPU code without running them. Track notes name
  the extra checks that also exist (C++ expected outputs, JavaScript syntax
  checks, statistics fence parity).
- `walkthrough_outputs_checked`: true exactly when the track uses at least one
  ordinary CI group and a recorded CI run qualified every one of them. Tracks
  with no ordinary group (core python, sql and bridge, dax, cuda, docker,
  kubernetes and spark-deployment) record false and carry no evidence.
- `evidence`: present exactly when `walkthrough_outputs_checked` is true. It
  holds `ci_run` (the `app-build.yml` run database ID), `commit` (that run's full
  head SHA) and `groups` (the ordinary CI groups the track uses, all of which
  concluded `success` in their job and `Qualify complete references` step).

| Route                 | Applies to                             | Label                            |
| --------------------- | -------------------------------------- | -------------------------------- |
| `course-check`        | Core python, sql and bridge lessons    | complete artifact executed       |
| `reference-corpus`    | Ordinary profiles run by the CI corpus | complete artifact executed       |
| `browser-workflow`    | `html-browser`, `javascript-browser`   | representative behavior executed |
| `kubernetes-workflow` | `k8s-kind`                             | representative behavior executed |
| `hand-derived`        | `dax-offline`                          | structure validated              |
| `reading-only`        | `reading`                              | structure validated              |
| `gpu-separate`        | GPU profiles                           | not validated on this platform   |

## Walkthrough routes

| Route          | Tracks                                                   |
| -------------- | -------------------------------------------------------- |
| `live-python`  | Core python and bridge (the live Python line tracer)     |
| `live-sql`     | Core sql (the live SQL clause planner)                   |
| `hand-derived` | dax (the existing hand-derived reference adapter)        |
| `authored`     | Every other track with ordinary-profile runnable lessons |
| `na`           | cuda, docker, kubernetes and spark-deployment            |

Live tracing is limited to the core Python and SQL lessons. No universal
automatic tracer exists, and no record, label or document may claim one. An
authored track records a `floor` equal to the number of stages that contain an
ordinary-profile lesson (3 today). R9 `pass` on an authored track requires
`courses/<track>/walkthroughs.json` to cover each of those stages.

## Recording CI evidence

`scripts/record_track_runtime_evidence.py --run RUN` reads one `app-build.yml`
run and records `runtime.evidence`, `walkthrough_outputs_checked: true` and an
R10 `pass` for every track whose ordinary CI groups all succeeded. The run's
commit must be available locally, and the course content and reference checker
in the working tree must equal that commit. `--dry-run` prints the plan and
writes nothing.

Every recorded track cites run 45399494825 at commit
`0770e8fd4c58030c20d8267ed3820eb630d1442f`. The 2.0.0 release commit
(`a4354ff8bf50bd2ea48d7eff2c130b75fb34dcc6`) later changed runtime files
(Spark 4.3.0, torch 2.15.0, Debian 13 Python). Its `app-build.yml` run skipped
the ordinary qualification jobs because the commit was marked for publication,
so the recorder has no newer run to read. The same references, walkthrough
expected outputs included, were qualified on amd64 and arm64 by the release
publish run 45460757558 before any image was promoted. The recorder does not
read publish runs, so that run is not cited in the ledger.

## Current results

All 40 tracks meet the threshold with no accepted gaps. R1 to R5, R8 and R10 are
`pass` everywhere. R6 and R7 are `na` only for tracks made entirely of tutorial
lessons, and R9 is `na` only for tracks with no ordinary-profile runnable lesson.
R11 is `not-assessed` on every track because no named person has reviewed one.

| Track                       | Threshold met | Accepted gaps | `na` criteria | CI groups in evidence                               |
| --------------------------- | ------------- | ------------- | ------------- | --------------------------------------------------- |
| `advanced-spark-modeling`   | yes           | none          | R6, R7        | scala-spark                                         |
| `apache-data-platforms`     | yes           | none          | R6, R7        | data-platforms                                      |
| `applied-science`           | yes           | none          | R6, R7        | python-core                                         |
| `bayesian-computing`        | yes           | none          | R6, R7        | bayesian, python-core, stan                         |
| `bridge`                    | yes           | none          | none          | none (no ordinary group)                            |
| `c`                         | yes           | none          | none          | c-go                                                |
| `cpp`                       | yes           | none          | none          | cpp                                                 |
| `csharp`                    | yes           | none          | none          | csharp                                              |
| `cuda`                      | yes           | none          | R9            | none (no ordinary group)                            |
| `custom-likelihood-pytorch` | yes           | none          | R6, R7        | pytorch                                             |
| `data-ml-engineering`       | yes           | none          | R6, R7        | data-engineering, python-core, pytorch, scala-spark |
| `data-visualization`        | yes           | none          | none          | python-core                                         |
| `dax`                       | yes           | none          | none          | none (no ordinary group)                            |
| `dbt`                       | yes           | none          | none          | data-engineering                                    |
| `deep-learning-pytorch`     | yes           | none          | none          | pytorch                                             |
| `deep-learning-tensorflow`  | yes           | none          | none          | python-core, tensorflow                             |
| `docker`                    | yes           | none          | R9            | none (no ordinary group)                            |
| `go`                        | yes           | none          | none          | c-go                                                |
| `java`                      | yes           | none          | none          | java                                                |
| `javascript-typescript`     | yes           | none          | none          | javascript-typescript                               |
| `jax`                       | yes           | none          | none          | jax                                                 |
| `julia`                     | yes           | none          | none          | julia                                               |
| `kubernetes`                | yes           | none          | R9            | none (no ordinary group)                            |
| `llm-applied`               | yes           | none          | none          | python-core, pytorch                                |
| `llm-evaluation`            | yes           | none          | none          | python-core, pytorch                                |
| `llm-theory`                | yes           | none          | none          | python-core, pytorch                                |
| `ml-engineering`            | yes           | none          | none          | data-engineering                                    |
| `nlp`                       | yes           | none          | none          | python-core                                         |
| `polars`                    | yes           | none          | none          | data-engineering                                    |
| `python`                    | yes           | none          | none          | none (no ordinary group)                            |
| `python-web`                | yes           | none          | R6, R7        | python-web                                          |
| `r`                         | yes           | none          | none          | r                                                   |
| `rust`                      | yes           | none          | none          | data-platforms                                      |
| `scala-spark`               | yes           | none          | none          | scala-spark                                         |
| `spark-deployment`          | yes           | none          | R6, R7, R9    | none (no ordinary group)                            |
| `sql`                       | yes           | none          | none          | none (no ordinary group)                            |
| `statistics-ml`             | yes           | none          | R6, R7        | bayesian, python-core                               |
| `swift`                     | yes           | none          | none          | swift                                               |
| `tmb-modeling`              | yes           | none          | R6, R7        | r                                                   |
| `web-development`           | yes           | none          | none          | php                                                 |

## Running the checks

```sh
.venv/bin/python scripts/check_track_qualification.py --track go
.venv/bin/python scripts/check_track_qualification.py --check
```

`--track` prints each criterion with its measured count, the runtime ledger, any
consistency errors and the reasons the track is below threshold. `--check`
validates every record and exits 1 on any inconsistency. Neither mode writes
files. After content changes, regenerate the matrix through its owning workflow,
then run `--check` and edit the affected records by hand.
