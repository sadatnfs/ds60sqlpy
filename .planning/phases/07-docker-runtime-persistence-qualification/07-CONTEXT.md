# Phase 7 context: Docker runtime and persistence qualification

## Requirements

- RUN-01: Every Docker image profile included in a release builds from the
  intended repository revision for its supported architectures and passes its
  documented startup and operation checks.
- RUN-02: Fresh setup, resume, stop, and restart behavior are verified with
  disposable Compose projects, and saved learner data remains intact.

Primary input: `07-RESEARCH.md` (2026-11-21). Release set: `app` plus 25
ordinary worker profiles (`docker/classroom-images.tsv`, GPU filtered out at
`scripts/docker_release.py:175`), for `amd64` and `arm64`
(`scripts/docker_release.py:50`), qualified in 19 CI groups
(`docker/ci-profile-groups.json`) on native runners
(`scripts/ci_profiles.py:13`). "Documented checks" means
`scripts/ci_classroom.py::required_checks` (lines 29 to 68); there is no second
list.

## Decisions

- **D-01 Plan breakdown.** Follow the research's four plans:
  07-01 revision binding (wave 1), 07-02 lifecycle harness (wave 1),
  07-03 two-architecture CI qualification (wave 2, after 07-01 and 07-02),
  07-04 evidence ledger in `07-VERIFICATION.md` (wave 3). 07-01 and 07-02 own
  disjoint files so they can run in parallel; `docs/validation.md` belongs to
  07-01 in wave 1, the lifecycle and runtime-qualification documentation lands
  in 07-03, and no Phase 7 plan edits `scripts/ci_classroom.py` (the launcher
  it drives computes the revision itself).
- **D-02 Revision binding.** Images carry OCI labels set through build args:
  `org.opencontainers.image.revision` from `ARG DS60_SOURCE_REVISION` in the
  root `Dockerfile` and every `docker/workers/Dockerfile.*`;
  `org.opencontainers.image.version` from `ARG DS60_RELEASE_VERSION` in worker
  Dockerfiles (the root `Dockerfile` keeps its existing literal version label at
  line 13 because `scripts/docker_release.py:634-638` gates it against
  `pyproject.toml`); `org.opencontainers.image.source` set to
  `https://github.com/sadatnfs/ds60sqlpy` in every image. The local build
  scripts (`scripts/classroom.sh`, which CI drives through
  `scripts/ci_classroom.py::launcher`) populate the args: the 40-hex
  `git rev-parse HEAD` for a clean tree, `<sha>-dirty` for a dirty tree, empty
  when git is unavailable. A verifier script inspects an image and asserts the
  revision label equals a given commit, rejecting empty and `-dirty` values.
- **D-03 Clean source for qualification.** Builds used as qualification
  evidence come from a clean `git worktree` of the target commit (locally) or
  a clean CI checkout of `github.sha`, never the shared dirty checkout that
  other agents are editing. Add `.planning` to `.dockerignore` (`work` is
  already excluded at `.dockerignore` line 21).
- **D-04 Lifecycle isolation.** The lifecycle harness uses disposable Compose
  projects named `ds60-p7-...`, image tags `<pyproject version>-p7<sha8>` (for
  example `1.4.3-p7a1b2c3d4`) that never clobber the shared tags
  `ds60sqlpy-lab:1.4.3` or `ds60sqlpy-worker-python-core:1.4.3`, ephemeral
  ports (`--port 0 --database-port 0`), and an ownership marker file checked
  before any `down -v`. Locally it runs the starter profiles only.
- **D-05 Lifecycle coverage.** The harness proves fresh setup, stop then
  resume, a rerun of `./classroom` (while running and after stop), container
  removal and recreate, and `--rebuild` with volumes kept, asserting that
  learner `progress.json`, saved drafts (pads) and run receipts, and a
  learner-created SQL table survive every transition.
- **D-06 Two-architecture CI.** A new `workflow_dispatch` workflow runs every
  profile group on native `amd64` and `arm64` runners at one commit. No QEMU,
  no `buildx --platform` emulation, matching the refusal in
  `scripts/ci_classroom.py:189-192`. No Docker Hub credentials or writes.
- **D-07 Revision to qualify.** Qualify the branch tip after 07-01 and 07-02
  have landed and after Phases 3 to 6 content is committed, so Phases 8 and 10
  inherit the same revision. A later content change requires re-dispatching
  07-03.
- **D-08 Exclusions, with reasons.** GPU profiles (`cuda-cpp`, `cuda-python`,
  `pytorch-cuda`, `tensorflow-cuda`): no GPU runners, and they are excluded
  from release at `scripts/docker_release.py:175`. Kubernetes images
  (`docker/kubernetes/Dockerfile.*`, `kubernetes.yml`): a separate non-release
  image family. Docker daemon restarts: cannot be performed safely on the
  shared host without disrupting protected containers.
- **D-09 Safety.** Never touch the user's `ds60-classroom` Compose project or
  its volumes (`ds60-classroom_classroom-learning`,
  `ds60-classroom_classroom-runtime`, `ds60-classroom_postgres-data`), the
  `ds60-phase1-browser` stack, `ds60-livetest-pg`, the `awesome-copilot` MCP
  containers, or the containers `tender_feistel` and `condescending_kirch`.
  Harness cleanup runs `down -v` only on a project carrying its own ownership
  marker. Never run any Docker pruning subcommand, and never restart Docker
  Desktop.
- **D-10 Caches and logs.** Keep caches, worktrees, reports and logs outside
  the repo (for example `~/.cache/ds60sqlpy/`) or under `work/` (gitignored at
  `.gitignore` line 14).
- **D-11 GitHub authority.** Pushing to `sadatnfs/ds60sqlpy` `main` and
  dispatching workflows is authorized. Authenticate with
  `export GH_TOKEN=$(env -u GH_TOKEN gh auth token --user sadatnfs)`.
- **D-12 Style.** No em or en dashes in any written file; American English.
- **D-13 Verification commands.**
  `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp <files>`,
  `.venv/bin/ruff check src scripts tests`,
  `.venv/bin/ruff format --check src scripts tests`, `.venv/bin/mypy src`, and
  `set -a; . ./.env; set +a; ./scripts/lint-repo` for shell and workflow lint.

## the agent's Discretion (choices made by the planner)

- Script and file names: `scripts/verify_image_revision.py`,
  `tests/test_image_revision.py`, `scripts/check_classroom_lifecycle.py`,
  `tests/test_classroom_lifecycle.py`,
  `.github/workflows/runtime-qualification.yml`,
  `tests/test_runtime_qualification_workflow.py`.
- Image update proof: the harness starts the project at a base revision
  (default the target's first parent) inside its own worktree, then checks out
  the target revision in that worktree and runs `./classroom --rebuild`. The
  revision label alone gives the two builds different image IDs, so the update
  step proves a real image change, not a retag. The tag scheme of D-04 yields
  two tags, `-p7<base8>` and `-p7<target8>`.
- The learner SQL object is created through the classroom SQL pad (`run`
  action, course role, `public` schema, which the course role may write per
  `docker/init/01-course-role.sql:17`), not through an admin session, so it is
  genuinely learner-created. Successful SQL runs commit
  (`src/ds60sqlpy/execution.py:263`).
- CI runs the lifecycle harness in a separate two-job (`amd64`, `arm64`)
  matrix inside the dispatch workflow instead of lengthening the python-core
  job.
- Commit messages for this phase must not contain `[publish-` or
  `[build-test-` markers, so a push to `main` never triggers publication or a
  targeted build (`.github/workflows/targeted-images.yml:11-16`,
  `.github/workflows/publish-images.yml:18`).
- `scripts/docker_release.py::inspected_image` gains a revision-label
  consistency check against `Context.revision` before staging (research Q2,
  item 4).

## Deferred Ideas (out of scope)

- Docker Hub promotion, release notes and version bump (Phase 10).
- Vulnerability, secret and SBOM scanning (Phase 8).
- GPU and CUDA profile qualification, Kubernetes runtime images, Docker
  daemon or Docker Desktop restart testing (D-08).
- Wiring the revision verifier into `app-build.yml`, `targeted-images.yml` or
  `publish-images.yml`.

## MVP note

ROADMAP marks Phase 7 `Mode: mvp`, but its Goal line is outcome-shaped, not a
user story. Plans quote the Goal verbatim rather than inventing a story; run
`/gsd-mvp-phase 7` if a user-story framing is required.
