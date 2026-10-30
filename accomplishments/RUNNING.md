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
- **Native Spark TMBad 0.2.0 passed a source-bound hosted two-platform run.**
  Source `400cbc03f376f6a1950bc7a7c9036bd6ed80633a`, workflow run
  `41092772765`, completed native AMD64 and ARM64 package, numerical and
  worker-loss checks. Evidence tier: exact-run hosted native qualification.
  Remaining gate: distinct classroom image publication, fresh Hub pull and
  learner resume acceptance. See `packages/spark-tmbad/README.md`.
- **Original R build logs stayed complete while repeated console diagnostics
  were condensed.** At source `006599ab2d1ff1acab3686c291a727b5704d1de3`,
  hosted run `40991855886` retained full compressed R build logs and bounded
  console summaries. Evidence tier: source-bound run artifacts, not a recurring
  guarantee. See `docker/workers/r/install_packages.py` and
  `tests/test_r_build_logging.py`.
- **Optional R/TMB/glmmTMB 24-case reference passed both native platforms.**
  At source `53b33b02d99ac615b992127228cbb9a463b7ceef`, hosted run
  `41122123106` passed 24/24 registered cases on AMD64 and ARM64, including
  the previously failed nonlinear-growth case. The AMD64 fit used a genuine
  status-0 L-BFGS-B restart from a guarded Newton seed; the score, Hessian and
  restoration checks remained in force. Evidence tier: exact-source hosted
  native qualification. The earlier AMD64 failure and local ARM64 v2 receipts
  remain historical. See `packages/spark-tmbad/reference/README.md`.
- **Independent Spark/PyTorch executor training is integrated as package
  0.2.0 source and locally qualified from one wheel.** The copied integrated
  wheel SHA256 `c40c06e0d78bdd8f8fbc2abb8c3e49deb59d77d8e786523af2193ea551d828a3`
  passed native ARM64 single- and two-executor SGD controls, typed Spark
  DataFrame shard coverage, actual worker loss, explicit checkpoint resume and
  model/optimizer/RNG continuation. Evidence tier: source-bound local native
  runtime. Remaining gate: neutral default-image hosted AMD64/ARM64
  qualification, exact-source Course CI and release publication. See
  `packages/spark-likelihood/docs/CPU-TORCH-TRAINING.md`.
- **Intermediate classroom 1.2.0 publication did not promote images.** At
  source `975a275f707dce29f0125ea23cddca17f6518b24`, publisher run
  `41111775724` retained 30 accepted jobs and nine late artifact-fetch
  failures before those worker builds. No canonical promotion was accepted.
  The final publication plan is consolidated as 1.3.0 and still requires its
  own exact-source gates, promotion and fresh pull/resume audit. See
  `docs/dockerhub.md` and `scripts/ci_release_artifacts.py`.

## Maintenance rule

Append a dated entry when a meaningful source, test, native runtime,
publication, browser or recurrence gate changes. Name the version or source
identity, evidence tier, and remaining gate. Do not rewrite earlier entries
to make historical results look current. Rebuild the lookup inventory after
registered sources change; rebuilding does not modify this file.
