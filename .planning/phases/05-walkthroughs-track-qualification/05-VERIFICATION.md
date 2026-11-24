---
phase: 05-walkthroughs-track-qualification
type: verification
status: passed
verified: 2026-11-24
score: 3/3 success criteria
covered_files:
  - .planning/phases/05-walkthroughs-track-qualification/05-01-PLAN.md
  - .planning/phases/05-walkthroughs-track-qualification/05-01-SUMMARY.md
  - .planning/phases/05-walkthroughs-track-qualification/05-02-PLAN.md
  - .planning/phases/05-walkthroughs-track-qualification/05-02-SUMMARY.md
  - .planning/phases/05-walkthroughs-track-qualification/05-03-PLAN.md
  - .planning/phases/05-walkthroughs-track-qualification/05-03-SUMMARY.md
  - .planning/phases/05-walkthroughs-track-qualification/05-04-PLAN.md
  - .planning/phases/05-walkthroughs-track-qualification/05-04-SUMMARY.md
  - .planning/phases/05-walkthroughs-track-qualification/05-05-PLAN.md
  - .planning/phases/05-walkthroughs-track-qualification/05-05-SUMMARY.md
  - curriculum/track-qualification.json
  - scripts/build_coverage_matrix.py
  - scripts/check_track_qualification.py
  - scripts/check_walkthroughs.py
  - scripts/record_track_runtime_evidence.py
  - tests/test_record_track_runtime_evidence.py
  - tests/test_track_qualification.py
covered_digest: v4:sha256:047e6bea60011c7f9a18da337f1cba22100a49ba10feda860275016ac361e4fe
---

# Phase 5 verification: walkthroughs and track qualification

Requirements: WALK-03, CURR-05, CURR-06. Plans 05-01 to 05-05 all have SUMMARYs.

## Commands rerun at closeout

| Command | Output |
| --- | --- |
| `python scripts/check_walkthroughs.py --check` | `OK: 96 authored walkthroughs across 32 tracks; nothing executed.` |
| `python scripts/check_track_qualification.py --check` | `OK 40 track records are consistent.` and `Threshold met by 40 of 40 tracks.` |
| `pytest tests/test_track_qualification.py tests/test_record_track_runtime_evidence.py` | part of the closeout full suite (5838 passed, 514 skipped) |

## Success criteria

| # | Criterion | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | Tracks that benefit from a walkthrough have tested adapter behavior or authored steps, without claiming universal tracing (WALK-03) | PASS | Live adapters for Python and SQL, a hand-derived DAX adapter, and 96 authored walkthroughs (3 stages each) for 32 tracks. R9 is `pass` on 36 tracks and a justified `na` on the 4 with no ordinary-profile runnable lesson. The classroom labels authored steps as authored, and Phase 9 browser check 18 opens and steps `go-001` without a run. |
| 2 | Runnable examples match their explanation in the registered runtime; unsupported capabilities are named (CURR-05) | PASS | R10 is `pass` on all 40 tracks from Course qualification run 45399494825 at `0770e8fd`, where all 19 CI groups succeeded on amd64 and arm64. `check_module_references` covers 1356 implementations, 96 of them with walkthrough expected output. The 2.0.0 Publish run 45460757558 re-qualified the same references on both arches at `a4354ff8` before promotion. Tracks without an ordinary runtime (`bridge`, `cuda`, `dax`, `docker`, `kubernetes` and others) are recorded as having no ordinary CI group. |
| 3 | Every track has a recorded rubric result at its threshold, with `na` and gaps justified (CURR-06) | PASS | `curriculum/track-qualification.json` holds 40 records. R1 to R5, R8 and R10 `pass` 40; R6 and R7 `na` 10, `pass` 30; R9 `pass` 36, `na` 4; R11 `not-assessed` 40, which D-03 and D-04 allow. No accepted gaps. R8 baseline commit `b1847ca7`. `docs/track-qualification.md` publishes the table. |

## Limits

- R11 needs a named human reviewer and has not been done for any track.
- Walkthrough prose is authored text. `check_walkthroughs` validates structure and stage
  coverage and executes nothing; the expected outputs are checked by the reference runs.
- The R10 ledger cites the `0770e8fd` run. It predates the 2.0.0 pin bumps (Spark 4.3.0,
  torch 2.15.0, Debian 13 Python); the newer evidence is the Publish run, which the recorder
  does not read.
