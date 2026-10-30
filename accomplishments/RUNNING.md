# Running accomplishments

This log is edited by a maintainer. The source-derived `INDEX.md` and
`inventory.json` are rebuilt separately. Each entry names the evidence tier
and its remaining gate so a source change is not confused with publication or
learner acceptance.
The [qualification summary](qualification-2026-10-30.json) records the exact
source revisions, hosted runs, artifact hashes and limits for this completion.

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
  the previously failed nonlinear-growth case. AMD64 first had an unsuccessful
  nlminb attempt, then accepted a genuine status-0 L-BFGS-B refinement with
  the original score, positive-definite Hessian and restored-objective checks.
  ARM64 accepted its first nlminb attempt. Neither actual case used a Newton
  seed; both image builds separately passed the guarded Newton-seed positive
  and refusal controls. Evidence tier: exact-source hosted
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

- **Classroom 1.3.0 source completed independent hosted build gates while
  publication remained pending.** At source
  `0db974c6d021a0bce5b9260577c122ad29bca876`, Application builds run
  `41139388006` completed its portable starter job, and standalone
  Spark/PyTorch run `41139477838` completed native AMD64 and ARM64
  builds, installed/offline checks, likelihood worker-loss recovery and
  executor-training/checkpoint/DataFrame cases. Evidence tier: exact-source
  hosted build/runtime checks. Course validation run `41139388074` passed
  all seven required jobs; its optional advanced imports job was skipped.
  Publisher run `41139387934` passed all 36 native ordinary worker build
  and qualification steps, alongside both App/Core seed jobs. Combined
  scientific checks, canonical promotion and fresh Hub acceptance still
  require final readback; no canonical
  promotion or fresh Docker Hub pull/resume is claimed here. An exact local
  maintenance readback at 23:26 UTC found zero running containers, all 40
  protected containers and 51 protected volumes present, and all 65 protected
  images among 67 retained images. The Linux overlayfs engine and reviewed
  disk expansion were recorded with a complete supported snapshot. The local
  deliverables assembly made no Docker state changes.

- **The repository now has a maintained lookup for future Codex work.**
  `accomplishments/INDEX.md` and `inventory.json` index 2,277 registered
  lessons, variants, packages, models, APIs, capabilities and study IDs.
  `index.py build`, `check` and `search` keep the generated lookup tied to its
  sources; this running log retains dated evidence separately. The index is
  included in the portable starter and source package and linked from agent
  and contributor guidance. Planned studies remain marked as planned.
- **Spark deployment teaching now covers the full submission route.**
  `courses/spark-deployment/` covers Compose and Kubernetes, batch submission,
  Jupyter sessions, custom images, driver and executor networking, ports,
  secure live UI access, History Server and event logs, storage, credentials,
  RBAC, resources and troubleshooting. The owned Compose lab is separate from
  cloud instructions. Authored Kubernetes guidance is not a cloud deployment
  acceptance claim.
- **Supported standalone and inline source formatting was completed.**
  Guarded formatting preserves executable meaning, mathematical expressions
  and retained runtime evidence. The generated accomplishment lookup precedes
  shared guide, TeX and reader generation. The final ordered generation
  produced 201 readers with 6,550 references and 3,519 TeX expressions.
  Current-source hosted formatting acceptance remains separately recorded by
  Course validation.
- **Independent modeling and CPU training packages are distributable.**
  `packages/spark-tmbad/` includes the 23-model native registry, Python and
  Scala entrypoints, named Gaussian priors, exact proximal L1 penalties,
  fixed-coordinate and prepared-point interfaces, prediction and forecasting.
  `packages/spark-likelihood/` installs the original likelihood API and the
  separate `ds60_torch_training` namespace in one 0.2.0 distribution, with
  explicit single-executor and two-rank CPU execution, supported normal Torch
  model/loss/optimizer usage, immutable DataFrame shards and explicit resume.
  Both folders include their own build, dependency, example and documentation
  routes. MAP estimates are not posterior samples; accepted bounded execution
  does not establish arbitrary-program or unlimited-scale support.

## Maintenance rule

Append a dated entry when a meaningful source, test, native runtime,
publication, browser or recurrence gate changes. Name the version or source
identity, evidence tier, and remaining gate. Do not rewrite earlier entries
to make historical results look current. Rebuild the lookup inventory after
registered sources change; rebuilding does not modify this file.
