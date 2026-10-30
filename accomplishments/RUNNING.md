# Running accomplishments

This log is edited by a maintainer. The source-derived `INDEX.md` and
`inventory.json` are rebuilt separately. Each entry names the evidence tier
and its remaining gate so a source change is not confused with publication or
learner acceptance.

## 2026-10-30

- **Classroom 1.2.0 source prepared.** The checked-in course, formatting,
  package and workflow changes have a marked release source. Evidence tier:
  repository source and focused local checks. Remaining gate: successful
  exact-source Course CI, full image promotion, fresh Hub pull/start/resume and
  all-module audit. See `docs/dockerhub.md` and `docs/validation.md`.
- **Independent native Spark TMBad package 0.2.0 qualified on both native Linux
  architectures.** The retained standalone workflow artifacts show installed
  Python and Scala checks, actual native numerical oracles, and a controlled
  worker-loss Compose recovery. Evidence tier: source-bound native runtime
  artifacts. Remaining gate: distinct classroom image publication and fresh
  Hub pull acceptance. See `packages/spark-tmbad/README.md`.
- **Optional R/TMB/glmmTMB comparison has 24 hash-bound ARM64 v2 cases.**
  Evidence tier: historical local reference receipts. Remaining gate: hosted
  native recurrence for the current recipe. See
  `packages/spark-tmbad/reference/qualification/index-v2.json`.
- **The newer hosted optional R source has one accepted native architecture.**
  At source `a86150cf`, ARM64 passed all 24 serial reference cases with complete
  package build logs and model compilation receipts. AMD64 completed 23 of 24;
  its nonlinear growth fit failed the original optimizer status and score
  checks. Evidence tier: exact-source hosted ARM64 success plus retained AMD64
  failure. Remaining gate: a new source-bound AMD64 qualification before any
  two-platform claim. This does not rewrite the earlier local v2 receipts.
- **Simulation studies are indexed by reserved `sim-001` through `sim-037`.**
  Source status varies by ID. Some have bounded historical local shards, some
  have only source or a design. This is not a blanket Monte Carlo calibration
  claim. See `packages/spark-tmbad/studies/design/studies.json`.
- **CPU Spark/Torch executor training is a work-only draft.** Pure safety
  checks and a direct CPU optimizer continuation have passed. The public
  single-distribution wheel, installed isolation, two-executor recovery and
  published source acceptance are pending. Keep this entry outside the
  generated repository inventory until the package is actually integrated.

## Maintenance rule

Append a dated entry when a meaningful source, test, native runtime,
publication, browser or recurrence gate changes. Name the version or source
identity, evidence tier, and remaining gate. Do not rewrite earlier entries
to make historical results look current. Rebuild the lookup inventory after
registered sources change; rebuilding does not modify this file.
