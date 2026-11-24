---
phase: 07-docker-runtime-persistence-qualification
plan: 04
subsystem: ci-runtime-qualification
status: complete
requirements: [RUN-01, RUN-02]
tags: [ci, docker, native-arm64, qualification, lifecycle, ledger]
requires: [07-01, 07-02, 07-03]
provides:
  - .planning/phases/07-docker-runtime-persistence-qualification/07-VERIFICATION.md (evidence ledger, RUN-01 PASS, RUN-02 PASS)
affects: [08-04, 10-01]
key-files:
  created:
    - .planning/phases/07-docker-runtime-persistence-qualification/07-VERIFICATION.md
    - .planning/phases/07-docker-runtime-persistence-qualification/07-04-SUMMARY.md
  modified: []
decisions:
  - The ledger is generated from downloaded artifacts by a scratch reader under work/ (not tracked), so every row is copied from evidence.
  - The qualified SHA is 6be2ffd4 (torch 2.15.0); the earlier dispatch on 46dc32fc was superseded by the torch CVE upgrade.
  - The local lifecycle stays seeded on 46dc32fc with update skipped; both CI lifecycle runs prove the update rebuild at the exact SHA.
commits: 1
actuals:
  tasks: 2
  commits: 1
completed: 2026-11-24
---

# Phase 7 Plan 04: Evidence ledger for runtime qualification Summary

`07-VERIFICATION.md` ties every ordinary image, group job and lifecycle step to one commit and
one workflow run, and gives evidence-backed verdicts: RUN-01 PASS and RUN-02 PASS.

- Ledger: `.planning/phases/07-docker-runtime-persistence-qualification/07-VERIFICATION.md`
- SHA: `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb`
- Run: [45390263162](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45390263162), conclusion `success` (38 group jobs plus 2 lifecycle jobs)
- Verdicts: RUN-01 PASS, RUN-02 PASS

## What was done

Task 1 (tracer): the evidence path was proven end to end. `gh run view --json` wrote
`work/p7-evidence/45390263162/run.json`, `gh run download` fetched the 40 artifact
directories, and the reader produced the first sourced row in each table.

Task 2: every row was generated from the same evidence and cross-checked.
- 38 `image-revision.json` reports and 38 `ci-qualification.json` reports, both architectures.
- 124 image rows (one per profile per architecture), every revision label equal to the SHA.
- `run.json` `headSha` equals the frontmatter `sha`.
- Three lifecycle tables: local arm64 (seeded), CI amd64 and CI arm64 (build mode, all eight
  steps, including the real update rebuild from `46dc32fc` to `6be2ffd4`). Every report has
  `passed: true`, zero protected errors and no residue.
- Protected resources and Exclusions sections (GPU profiles, Kubernetes images, daemon restarts).

## Verification (real results)

| Check | Result |
| --- | --- |
| Required sections (RUN-01, RUN-02, Exclusions, Protected resources, Lifecycle) | all present |
| Newest evidence directory ID in the ledger | `45390263162` present |
| SHA length | 40 |
| `image-revision.json` count | 38 |
| SHA occurrences in the ledger | 166 (at least 39 required) |
| Em or en dashes in the ledger | 0 |
| RUN-01 and RUN-02 verdict lines | PASS, PASS |

## Deviations

1. CI mirror passthrough: `scripts/ci_classroom.py` keeps `DS60_PYTHON_INDEX_URL` and
   `DS60_NPM_REGISTRY` in the launcher environment it otherwise filters of `DS60_` keys, so
   qualification can run on restricted networks; hash-locked installs keep images identical.
2. Seeded local lifecycle: this Mac reaches Python packages only through the Microsoft proxy,
   which lacked the locked `certifi`, so the local run seeds the published images and skips
   `update` (recorded in the ledger). The CI lifecycle runs prove `update`.
3. Local target: the local run targets `46dc32fc`. The one commit after it, `6be2ffd4`, does
   not touch the services the local lifecycle exercises (note added to the ledger).
4. Prettier layout of `docker/workers/r/packages.lock.json` and
   `docker/workers/spark/jar-overrides.json`, required by the format gate.
5. PyTorch CVE fix: torch 2.9.1 moved to 2.15.0 with filelock 4.2.11. torch 2.10.0 was rejected
   because it still carries CVE-2025-3000.
6. `llm-torch-cpu` coverage added to 53 CVE policy entries for the new base.
7. Deep learning PyTorch course prose and tests updated for the new torch version.
8. Qualification re-dispatched on `6be2ffd4`; the dispatch on `46dc32fc` was superseded.
9. Course validation on `6be2ffd4` failed in two jobs, both fixed in `0770e8fd`:
   - Eight planning research fences were not in canonical form, so the inline fence formatter
     failed the format check.
   - `running()` in the Spark TMB and Torch cleanup checks raced a process reaped during the
     `/proc/<pid>/stat` read (`ProcessLookupError`). Both checks now treat it as stopped, and a
     regression test fails without the fix.

## Human check

Read the Verdicts section in `07-VERIFICATION.md` and confirm the RUN-01 and RUN-02 verdicts
match the tables and the exclusions are acceptable for the 2.0.0 release.
