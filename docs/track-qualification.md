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
solution 700 words). While the matrix has no `templated_words` metric, R8 cannot
be `pass` and is recorded as `gap`.

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
for each track. It is a strict expected failure until the Phase 5 closure plan
records final results, so an unexpected pass is reported as a failure and the
marker must then be removed.

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
- `guide_examples`: what checks the guide code. Guide code blocks are not executed
  in this phase; content rendering checks cover them. Track notes name the extra
  checks that do exist (C++ expected outputs, JavaScript syntax checks, statistics
  fence parity).
- `walkthrough_outputs_checked`: whether authored walkthrough expected outputs are
  confirmed against reference runs; false until the closure plan confirms it.

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
