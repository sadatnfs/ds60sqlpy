# Phase 7: Docker Runtime & Persistence Qualification - Research

**Researched:** 2026-11-21
**Domain:** Docker Compose classroom runtime, native multi-arch CI qualification, learner-data persistence across lifecycle transitions
**Confidence:** HIGH for inventory, CI topology and lifecycle code paths (read in source this session); MEDIUM for the harness design (new code, built on verified primitives); LOW only where tagged `[ASSUMED]`

<user_constraints>
## User Constraints

No `07-CONTEXT.md` exists. These constraints come from the orchestrator prompt, `.planning/STATE.md` and `.planning/PROJECT.md`. Treat them as locked.

### Locked Decisions
- Phase 7 proves RUN-01 (every supported image profile builds from the intended source revision for each supported architecture and passes its documented startup and operation checks) and RUN-02 (fresh setup, resume, stop and restart preserve saved learner data).
- Disposable projects only. Never touch the user's `ds60-classroom` project or its volumes (`ds60-classroom_classroom-learning`, `ds60-classroom_classroom-runtime`, `ds60-classroom_postgres-data`), the running `ds60-phase1-browser` stack (ports 55014/55015), `ds60-livetest-pg`, the awesome-copilot MCP containers, or the containers `tender_feistel` and `condescending_kirch`.
- `down -v` (or `--volumes`) may only ever target a project this phase created, under its own unique prefix.
- GitHub Actions on `sadatnfs/ds60sqlpy` may be used. Pushing branches and dispatching workflows is authorized.
- Phase 7 does not publish to Docker Hub. Publication is Phase 10 (REL-01/REL-02). Phase 8 (SEC-01) consumes the image set Phase 7 qualifies.
- The working tree is shared with other agents (Phases 3 and 4 are editing). Do not rely on a clean tree in the primary checkout.

### the agent's Discretion
- Harness shape (new script vs. extension of `scripts/ci_classroom.py`), how revision provenance is recorded, local vs. CI split, and plan breakdown.

### Deferred Ideas (OUT OF SCOPE)
- GPU/CUDA profile qualification (not in the release set; see Q1).
- Docker Hub promotion, release notes, version bump (Phase 10).
- Vulnerability/secret/SBOM scanning (Phase 8).
- Kubernetes runtime (`kubernetes.yml`) beyond noting it is a separate, non-release image family.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RUN-01 | Every supported Docker image profile builds from the intended source revision for each supported architecture and passes its documented startup and operation checks. | Q1 inventory (26 release profiles x amd64/arm64, 19 CI groups, native runners only), Q2 revision binding gap (local images carry empty `revision` label), Q3 check catalogue (`ci_classroom.required_checks`), Plan 07-01 and 07-03 |
| RUN-02 | Fresh setup, resume, stop and restart preserve saved learner data across Docker image updates and normal classroom lifecycle transitions. | Q4 lifecycle map and gap list (only `down` + `--no-build` replacement is proven with real Docker; stop/resume, plain restart, `--rebuild` with retained volumes and progress.json/SQL learner objects are unproven), Q5 disposable harness, Plan 07-02 |
</phase_requirements>

## Summary

The classroom ships one app image (`ds60sqlpy-lab`) plus 25 ordinary worker profiles, and a release publishes exactly those 26 profiles for linux/amd64 and linux/arm64. The four GPU profiles are catalogued but excluded from release by `scripts/docker_release.py:175`. CI never emulates: every architecture is built and qualified on a native GitHub runner (`ubuntu-24.04` / `ubuntu-24.04-arm`), and `ci_classroom.prepare` refuses a non-native daemon outright. The ordinary push matrix (`app-build.yml`) only qualifies amd64; arm64 is qualified only by `targeted-images.yml` build-test markers (one group per push) or by the publish workflow. The last full both-arch qualification of all 19 groups was publish run 44798675803 on `c46e6ad4` (2026-11-20), which is not the current revision.

Source-revision binding exists only at publication time (Hub index annotations, candidate tags, `ci-qualification.json` summary). Locally and in ordinary CI, the image label `org.opencontainers.image.revision` is the empty string (`Dockerfile:12-18`) and worker Dockerfiles have no labels at all, so nobody can prove from an image which commit it came from. RUN-01 needs a revision label (build arg) plus a verifier, or at minimum an evidence record binding image ID to `git rev-parse HEAD` on a clean checkout.

Persistence is well designed (three named volumes, a launcher that resumes exact containers, a stable worker token), but real-Docker evidence covers only one transition: `compose down` (no `-v`) followed by a `--no-build` relaunch, in CI. Stop then resume, plain repeat start, `--rebuild` with retained volumes, and learner progress/SQL-object survival are proven only against a fake Docker CLI. Phase 7 should add a lifecycle harness that drives the real launcher through every transition on a `ds60-p7-*` project with an isolated image tag, run it locally on the starter profile set, and run it in CI on both native architectures.

**Primary recommendation:** Add `--label org.opencontainers.image.revision` via a build arg plus a `verify-image-revision` helper (07-01), add `scripts/check_classroom_lifecycle.py` that runs fresh, stop, resume, restart, recreate and rebuild against a disposable project with an ownership guard and a non-colliding image tag (07-02), then wire it into a new `workflow_dispatch` native both-arch matrix over all 19 groups and record run IDs at one revision (07-03).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Image build per profile/arch | CI (native GitHub runners) | Local Docker Desktop (starter only) | `ci_classroom.py:189-192` refuses emulation; this Mac is arm64 only with about 7.75 GiB engine memory |
| Revision binding | Build (Dockerfile ARG/LABEL) | Evidence ledger (JSON) | Label survives in the image; ledger binds image ID to commit for workers |
| Lifecycle orchestration | Launcher (`scripts/classroom.sh`) | Compose | Harness must drive the real learner entry point, not raw compose, to prove RUN-02 |
| Learner data | Docker named volumes | `.classroom/<project>/` host state | Pads/progress/runs in `classroom-learning`, DB in `postgres-data`, token in `classroom-runtime` |
| Operation checks | HTTP probes (`check_lab_http.py` etc.) | Browser (Playwright) | Existing checks already have `--check-persistence` modes |
| Cleanup safety | Harness ownership marker + name regex | Compose `-p` scoping | Same pattern as `ci_classroom.py:458-463` |

## Project Constraints (from .github/copilot-instructions.md)

- Supported product is the Linux-container Docker classroom; Windows goes through WSL 2 (docs/validation.md:15, :211).
- Never remove learning volumes to recover space; prune nothing that belongs to a learner project (docs/one-command-classroom.md:44, :173).
- Use `--confirm-disposable` and a never-used project name for any check that writes pads or resets SQL (docs/validation.md:332-353).
- Python 3.11 target, ruff line length 100, mypy strict (pyproject.toml `[tool.ruff]`, `[tool.mypy]`). New scripts must pass `make lint`/format via the pinned Docker formatter.
- Tests use pytest with `--strict-markers --dist=loadgroup` (pyproject.toml `[tool.pytest.ini_options]`).
- No secrets in logs or artifacts; `ci_classroom.clean_environment` strips DS60_*/COMPOSE_* and secret variables (ci_classroom.py:71-94). New harness must reuse it.

## Standard Stack

No new packages. Everything is in the repo or on the host.

### Core
| Tool | Version (observed) | Purpose | Why |
|------|-------------------|---------|-----|
| Docker Engine (Docker Desktop, context `desktop-linux`) | 29.9.3, arm64 `[VERIFIED: docker version]` | Local starter qualification | Already used by Phase 1 |
| Docker Compose plugin | 5.7.1 `[VERIFIED: docker compose version]` | Project-scoped lifecycle | Launcher calls `docker compose -p` |
| `scripts/classroom.sh` (`./classroom`) | repo HEAD | Real learner lifecycle | The RUN-02 subject |
| `scripts/ci_classroom.py` | repo HEAD | Existing disposable CI harness (prepare/qualify/cleanup) | Ownership marker, clean env, required checks |
| `scripts/check_lab_http.py` | repo HEAD | HTTP smoke plus `--check-persistence` | Already seeds and verifies pad/evidence/run receipt |
| pytest (+ xdist) | per `requirements` lock | Unit tests with fake docker | Existing `tests/test_classroom_launchers.py` fixture |
| GitHub Actions native runners | `ubuntu-24.04`, `ubuntu-24.04-arm` (ci_profiles.py:13) | Both-arch builds | No QEMU, no buildx multi-platform builds |
| `gh` CLI | present | Dispatch and collect run evidence | Authorized for this repo |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Native arm64 runners | buildx + QEMU | Rejected by policy: "emulation is not qualification" (ci_classroom.py:189-192) |
| New dispatch matrix | 19 `[build-test-<group>]` pushes | Works today, but one marker per commit and per-ref cancel-in-progress (targeted-images.yml:11-16) means 19 branches or 19 serial pushes |
| docker-bake | (none exists) | Not adopted in repo; do not introduce |

## Package Legitimacy Audit

This phase installs no external packages. Base images and per-arch locks are already pinned (`Dockerfile` uses `python:3.12.16-slim-bookworm` by digest; workers use `requirements-*.amd64.lock` / `requirements-*.arm64.lock`).

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | n/a | n/a | n/a | n/a | n/a | n/a |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Q1. Image inventory, release set, architectures, CI build method

### Catalogue (source of truth)
`docker/classroom-images.tsv:1` header, quoted verbatim: `# profile service local-repository published-suffix image-variable kind` `[VERIFIED: docker/classroom-images.tsv:1-31]`

| Kind | Profiles | Line(s) | Released? |
|------|----------|---------|-----------|
| `app` | `app` (service `lab`, repo `ds60sqlpy-lab`, variable `DS60_LAB_IMAGE`) | 2 | Yes |
| `ordinary` | python-core, cpp20, java21, javascript-node, typescript-node, tensorflow-cpu, llm-torch-cpu, scala-jvm, spark-local-scala, spark-local-python, c17, go, csharp-dotnet, rust-stable, swift-linux, php-cli, jax-cpu, bayesian-cpu, r-statistics, data-engineering, data-platforms-python, stan-cpu, julia, dbt-duckdb, python-web (25) | 3-31 excluding 19-22 | Yes |
| `gpu` | cuda-cpp, cuda-python, pytorch-cuda, tensorflow-cuda | 19-22 | No |

- Release filter: `if kind != "gpu": result[profile] = ...` `[VERIFIED: scripts/docker_release.py:175]`
- Architectures: `ARCHITECTURES = ("amd64", "arm64")` `[VERIFIED: scripts/docker_release.py:50]`
- Seeds: `SEEDS = frozenset({"app", "python-core"})` `[VERIFIED: scripts/docker_release.py:51]`
- `docker/ci-scientific-projects.json` declares `"ordinary_profile_count": 26` and the same two architectures `[VERIFIED: read this session]`.
- **Release set = 26 images x 2 architectures = 52 platform images, assembled into 26 two-platform indexes at promotion.**

### Dockerfiles
| File | Builds | Released |
|------|--------|----------|
| `Dockerfile` (root) | app/lab: multi-stage, Node TeX stage then `python:3.12.16-slim-bookworm` by digest | Yes |
| `docker/workers/Dockerfile.{python-core,python-web,cpp,c,go,java,node,php,csharp,swift,rust,spark,tensorflow,torch,jax,bayesian,stan,julia,r,data,data-platforms}` | ordinary workers (several profiles share a Dockerfile, e.g. node serves javascript-node and typescript-node; spark serves scala-jvm/spark-local-*) | Yes |
| `docker/workers/Dockerfile.cuda` | GPU profiles | No |
| `docker/kubernetes/Dockerfile.fixture`, `Dockerfile.worker` | Kubernetes runtime fixture, built in `kubernetes.yml:48-49`, amd64, dispatch/weekly | No |
| `docker/formatting/Dockerfile`, `Dockerfile.r` | Lint/format toolchain | No |
| Scientific project images (`spark-torch`, `spark-tmb`) | Built in publish job from staged worker digests as ephemeral tags `ds60-scientific-<run>-<attempt>-<arch>-<project>` (scripts/ci_scientific_projects.py:332, :366) | No (qualification only) |

No `docker-bake*.hcl` exists. CI sets `COMPOSE_BAKE=false` (ci_classroom.py:91).

### Compose files
| File | Role | Key lines |
|------|------|-----------|
| `compose.yaml` | postgres + lab base | pg healthcheck 21-25; lab healthcheck 54-59 |
| `compose.classroom.yaml` | classroom project (`name: ds60-classroom`, line 3), init, internal module network | volumes 220-223; learning mount 83-87 |
| `compose.modules.yaml` | worker services | `restart: on-failure` line 15; worker healthcheck 28-39 |
| `compose.classroom.kubernetes.yaml` | Kubernetes overlay | not release |

Note: `name: ds60-classroom` is a default only. The launcher always passes `-p <project>`, so a `--project ds60-p7-...` run gets its own `ds60-p7-..._classroom-learning` etc. volumes.

### CI groups and build method
`docker/ci-profile-groups.json` defines 19 groups: python-core, python-web, cpp, java, php, c-go, csharp, swift, javascript-typescript, scala-spark, tensorflow, pytorch, data-engineering (data-engineering + dbt-duckdb), stan, julia, jax, bayesian, r, data-platforms (data-platforms-python + rust-stable). `RUNNERS = {"amd64": "ubuntu-24.04", "arm64": "ubuntu-24.04-arm"}` `[VERIFIED: scripts/ci_profiles.py:13]`.

| Workflow | Trigger | Arch | What it builds/qualifies | Hub writes |
|----------|---------|------|--------------------------|-----------|
| `app-build.yml` | every push, PR, dispatch (mode `ordinary` for unmarked commits) | **amd64 only** (ubuntu-latest), lines 93-145, max-parallel 4, 150 min timeout | all 19 groups, `ci_classroom.py prepare/qualify/cleanup`, project `ds60-ci-<group>-<run_id>-<attempt>` | No |
| `targeted-images.yml` | push with HEAD marker `[build-test-<group>]` (ci_targeted_images.py:24) | amd64 + arm64 native | seed (app + core) lines 80-176, then that group lines 177-308 | No (build-test); `[publish-<group>]` writes |
| `publish-images.yml` | push to main with `[publish-docker]` (line 18) | amd64 + arm64 native | seed 50-136, all groups 138-258, scientific projects, promote, pull audit | Yes (Phase 10) |
| `verify-published-images.yml`, `audit-published-release.yml` | dispatch | both | pull audits of Hub | No |
| `kubernetes.yml` | dispatch/weekly | amd64 | k8s fixture images | No |

Evidence `[VERIFIED: gh run view]`:
- app-build run 45301514511 on `094358cc` (origin/main): all 19 amd64 groups green (python-core about 18 min, scala-spark about 35 min, r about 18 min).
- publish run 44798675803 on `c46e6ad4` (release 1.4.3): seeds about 17 min per arch; all 19 groups both arches green; scientific projects about 15 to 17 min; promote and pull audit green. Wall time about 78 minutes. This is the timing baseline for a full both-arch qualification.
- Last targeted build-test: run 41124262125 `[build-test-python-core]` (2026-10-30).
- Current HEAD `5ad22de5` (branch `checkpoint/classroom-guide-step-through-2026-11-20`) has no both-arch qualification.

## Q2. How source revision is pinned and verified

| Mechanism | Where | Binds revision? |
|-----------|-------|-----------------|
| App image LABEL | `Dockerfile:12-18`: `org.opencontainers.image.version="1.4.3"`, `org.opencontainers.image.revision=""`, `org.opencontainers.image.created=""` | **No (empty)** |
| Worker image labels | none in `docker/workers/Dockerfile.*` (grep empty) | **No** |
| Version gate | `inspected_image` requires app/core label version == pyproject version (docker_release.py:634-638); pyproject `version = "1.4.3"` (line 7) | Version only |
| Candidate tags | `ci-{revision}-{run_id}-{attempt}-{profile}-{arch}` (docker_release.py:266) | Yes, publish only |
| Index annotations | `org.opencontainers.image.revision` = `GITHUB_SHA`, plus version, source, `io.ds60.release.schema`, `io.ds60.release.profile` (docker_release.py:59-65, ~333-345) | Yes, publish only |
| GitHub context gate | push to main, HEAD == GITHUB_SHA, clean checkout (docker_release.py:200-251) | Yes, publish only |
| CI summary | `ci-qualification.json` records `revision` from `git rev-parse HEAD`, run_id, attempt (ci_classroom.py:446-456) | Yes, as evidence artifact, not in image |
| Launcher Hub check | verifies 40-hex revision annotation via `buildx imagetools inspect` (classroom_images.sh:304-315) | Hub images only |

**Gap:** an image built locally or in app-build/targeted-images cannot be traced to a commit from the image itself. Also `.dockerignore` excludes `.classroom/`, `work`, `.git` etc. but not `.planning/` or other uncommitted edits, so a build from the shared dirty checkout bakes uncommitted files into the image.

**Recommendation (07-01):**
1. Add `ARG DS60_SOURCE_REVISION=""` to the root Dockerfile and each worker Dockerfile, and `LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}"` `[ASSUMED: design choice]`. Placing the ARG/LABEL in the final stage after heavy layers keeps cache reuse; a label-only change does not invalidate earlier layers.
2. Pass it from the launcher's local build path and from `ci_classroom.launcher()` as `git rev-parse HEAD` only when `git status --porcelain` is empty; otherwise pass `<sha>-dirty` so a dirty build is visibly not a qualification candidate.
3. Add a verifier (`scripts/verify_image_revision.py` or a `docker_release.py inspect` mode) that asserts `docker image inspect -f '{{ index .Config.Labels "org.opencontainers.image.revision" }}'` equals the expected 40-hex sha for every selected profile.
4. Keep the publish path unchanged except asserting the label equals `GITHUB_SHA` before staging (cheap consistency check with the index annotation).
5. Build Phase 7 qualification images from a clean `git worktree add` of the target commit, never from the shared checkout.

Risk: the `created` label is intentionally empty for reproducibility; do not populate it.

## Q3. Startup and operation checks per profile

| Check | Location | Runs |
|-------|----------|------|
| Postgres healthcheck `pg_isready` | compose.yaml:21-25 | every start |
| Lab healthcheck (`docker/healthcheck.py`, GET `/classroom` with Host header) | compose.yaml:54-59 | every start |
| Worker healthcheck `:8081/health` with token | compose.modules.yaml:28-39 | every start |
| Launcher readiness: `exec -T lab python /opt/course/docker/healthcheck.py`, host curl, writes `classroom.url`, prints `Ready:` | classroom.sh:709, 713, 731 | every launcher start |
| `./classroom doctor` | classroom.sh actions | local and CI |
| `ci_classroom.required_checks` | ci_classroom.py:29-68: launcher doctor, `check_lab_http.py`, `check_classroom_profiles.py`, `check_classroom_failures.py`, `check_module_references.py`, the `:persistence` variants, group-specific browser and project checks | CI (app-build amd64, targeted/publish both arches) |
| `check_lab_http.py` | seeds python-01 pad `print(6 * 7)`, evidence note `HTTP smoke fixture; this is not learner mastery.`, run receipt (output 42) (lines 145-159); `--check-persistence` verifies they survived (87-105); SQL check is fixture row count on `training.customers` (136-144) | CI; locally by hand per docs/validation.md:332-409 |
| Browser (`check_classroom_browser.py`, D3, Plotly) | python-core group only | CI amd64; Phase 1 ran locally via `~/.cache/ds60sqlpy/run-browser.sh` |
| Scientific artifacts | python-core and r groups | CI |
| Scientific projects (spark-torch, spark-tmb) | publish only | CI both arches |

Local pytest suites are unit-level only (fake docker CLI on PATH): `tests/test_docker_classroom.py` (init token/volume semantics on tmp dirs, compose structure 352-497), `tests/test_classroom_launchers.py` (2004 lines), `tests/test_targeted_images.py` (marker logic), `tests/test_release_runtime_integration.py` (formatter/fake docker). None starts a real container.

**"Documented checks" for RUN-01 = `ci_classroom.required_checks(group)` for that group, on both native arches, at one revision.** That function is the single source; Phase 7 should not invent a second list.

## Q4. Lifecycle and persistence

### Entry points
- `./classroom` delegates to `scripts/classroom.sh`. `START_DOCKER_CLASSROOM.command` and `.cmd` call `classroom.cmd` (WSL). Makefile targets `docker`, `docker-stop`, `docker-status`, `classroom`, `classroom-build`, `classroom-start` (`--no-build`), `classroom-stop` (Makefile:70-97).
- Actions: `up|start|resume|build|pull|stop|status|logs|doctor|publish`. `resume` sets `no_build=1` (classroom.sh:167).
- `--project NAME` must match `^[a-z0-9][a-z0-9_-]{0,48}$`.
- `--port 0 --database-port 0` picks dynamic host ports.
- `--local-build --tag <version>` builds and tags locally as `$local_name:$profile_tag` (classroom_images.sh:215-233); `valid_image_version` (classroom_images.sh:22-24) accepts suffixed versions such as `0.4.1-test` (used at tests/test_classroom_launchers.py:1321-1325).

### Transitions
| Transition | Implementation | Expected data behavior |
|------------|---------------|------------------------|
| Fresh setup | `./classroom --starter` (or `--profile ...`), creates `.classroom/<project>/` state (classroom.sh:238): `selection.env`, `ports.env`, `images.env`, `gpu.env`, `classroom.url`, `launcher.lock` | creates 3 named volumes; init writes stable token |
| Stop | `compose -p <project> --profile '*' stop --timeout 20` (classroom.sh:451-453) | containers exited, volumes retained |
| Resume | `./classroom resume` → `start_existing`, poll health; config-hash drift fails unless `--rebuild` (~546-550); strict resume reports missing images (~604) | same container IDs; if dynamic browser port changed, lab recreated from same image (docs/one-command-classroom.md:89-95) |
| Plain restart (repeat `./classroom`) | `start_or_create` (649-668) | reuses exact containers without build/pull |
| Container removed, image present | recreate with same volumes | data retained |
| Update | `./classroom --local-build --rebuild` | new images, containers replaced, volumes retained (docs/one-command-classroom.md:119-125) |

### Where learner data lives
| Data | Location |
|------|----------|
| Pads, progress, run history | `classroom-learning` volume at `/workspace/.learning` in lab (compose.classroom.yaml:83-87): `.learning/pads/`, `.learning/progress.json`, `.learning/classroom-runs` |
| Worker token | `classroom-runtime` volume; `init_module_runtime.py` creates once, never rotates |
| SQL learner objects | `postgres-data` volume |
| Launcher selection/ports/images | host `.classroom/<project>/` (gitignored, .gitignore:55; dockerignored, .dockerignore:84) |

### Existing persistence evidence
- Real Docker, CI only: `ClassroomCI.replace()` runs `compose down` (no `-v`) then launcher `--no-build` (ci_classroom.py:232-236, called at 326 and 369), then the `:persistence` checks.
- Fake CLI only: stop scoping (tests/test_classroom_launchers.py:489), plain repeat resumes exact containers (762), strict resume (831), dynamic ports on restart (420), config change requires rebuild (881), replaced database repair (890), failed-rebuild state restore (1977).

### Gaps (none of these has a real-Docker test)
1. `./classroom stop` then `./classroom resume` preserving container IDs and data.
2. Plain repeat `./classroom` while running and after stop.
3. `--local-build --rebuild` with retained volumes (the "Docker image updates" clause of RUN-02).
4. Volume identity: no assertion that the same volume (name + CreatedAt) is mounted after each transition, or that the token is unchanged.
5. `progress.json` and module drafts are not checked; only the python-01 pad, evidence note and run receipt are.
6. Learner-created SQL objects: only the fixture count is checked; a learner's own table could be lost by a reseed without detection.
7. Dynamic-port lab recreate path on real Docker.
8. Daemon/engine restart (Docker Desktop restart). Treat as optional/manual; it cannot be done safely on this shared host.
9. arm64: the `replace` persistence path runs only in targeted/publish runs, never on ordinary pushes.

## Q5. Disposable harness design and local build bounds

### System architecture

```
operator / CI job
   │  (git worktree at target SHA, clean tree)
   ▼
check_classroom_lifecycle.py ──guard──► name regex ^ds60-(p7|ci)-[a-z0-9-]+$ + project absent + owner marker
   │
   ├─► ./classroom --project P --local-build --tag 1.4.3-p7<sha8> --port 0 --database-port 0 --no-browser --starter|--profile ...
   │        └─► docker compose -p P (volumes P_classroom-learning, P_classroom-runtime, P_postgres-data)
   │
   ├─► seed: check_lab_http.py --url (classroom.url) --confirm-disposable
   │         + psql sentinel table via `compose -p P exec -T postgres`
   │         + snapshot: container IDs, volume CreatedAt, token sha256, progress.json sha256
   │
   ├─► transition loop: stop → resume → repeat start → down(no -v)+start → --rebuild
   │        after each: --check-persistence probes + snapshot diff + sentinel query
   │
   ├─► evidence JSON (revision, image IDs + revision labels, per-step results)
   │
   └─► cleanup (finally): owner marker check → compose -p P down -v --remove-orphans
                          → rm .classroom/P → docker image rm only tags *:1.4.3-p7<sha8>
```

### Isolation rules (prescriptive)
- **Project name:** `ds60-p7-<sha8>-<6 random hex>` locally; in CI reuse `ds60-ci-<group>-<run_id>-<attempt>` because `ci_classroom.py:144` only admits `ds60-(?:ci|pub)-...`. Fits the 49-character launcher limit.
- **Refuse if the project exists:** check `docker compose ls -a`, `docker ps -a --filter label=com.docker.compose.project=P` and `docker volume ls --filter label=com.docker.compose.project=P` all empty before starting (same rule as ci_classroom.py:186-199).
- **Ownership marker:** write `.classroom/P/p7-owner.json` (pid, start time, revision) before first launch; cleanup proceeds only if it exists and matches. Mirrors `ci-owner.json`.
- **Image tag isolation (critical):** a plain `--local-build` tags `ds60sqlpy-lab:1.4.3` and `worker-python-core:1.4.3`, the exact tags the user's stopped `ds60-classroom` and the running `ds60-phase1-browser` were built from. Retagging them makes those projects' repair path fail ("The app image name now points to a different image") or silently resume onto the new image. Always pass `--tag 1.4.3-p7<sha8>`. `ci_classroom.py:146-148` rejects non-pyproject versions, so the local harness must call the launcher directly (or ci_classroom gains an explicit `--tag-suffix` that is only legal with a `ds60-p7-` project).
- **Ports:** `--port 0 --database-port 0`; read the URL from `.classroom/P/classroom.url`.
- **Never:** `docker system prune`, `docker volume prune`, `docker image prune`, `compose down` without `-p`, or any command naming `ds60-classroom`, `ds60-phase1-browser`, `ds60-livetest-pg`.
- **Environment:** reuse `ci_classroom.clean_environment` (strips DS60_*/COMPOSE_* and secrets, ports to 0).

### Local build bounds on this Mac
Observed `[VERIFIED: docker info / image ls / system df]`: arm64, 10 CPUs, about 7.75 GiB engine memory; `ds60sqlpy-lab:1.4.3` and `worker-python-core:1.4.3` are 2.35 GB each; images total 31.67 GB, build cache 23.43 GB, volumes 8.7 GB. The Phase 1 browser stack is running and uses memory.

| Scope | Local? | Reason |
|-------|--------|--------|
| app + python-core (`--starter`) | **Yes** | Warm build cache exists from Phase 1; CI seed takes about 17 min cold, expect less locally with cache |
| c-go, cpp, php, javascript-typescript, python-web | Optional, one at a time | CI group time 4 to 7 min each; modest images |
| scala-spark, r, data-engineering, data-platforms, julia, stan, tensorflow, pytorch, jax, bayesian, swift, java, csharp | **CI only** | 6 to 35 min per group on CI; large toolchains; memory pressure next to running stacks; adds tens of GB to an already 55 GB image+cache footprint |
| amd64 anything | **CI only** | Mac is arm64; emulation rejected by policy |

Bounding rules: one local project at a time; `--starter` only by default; wrap each launcher call in a timeout (fresh build 45 min, transitions 10 min each); check free disk before build (`docker system df`) and abort if image+cache growth would exceed a stated budget (for example 15 GB); remove only the `*:1.4.3-p7<sha8>` tags afterwards (layers stay in shared cache, which is fine).

### CI qualification for RUN-01 (both arches, all groups, one revision)
`ci_targeted_images.py` derives intent from a push event (lines 98-122) and allows one marker per commit (54-76); same-ref pushes cancel the in-flight build-test run (targeted-images.yml:11-16). Recommended: add a `workflow_dispatch` workflow (for example `.github/workflows/runtime-qualification.yml`) that:
1. Resolves `github.sha`, asserts a clean checkout.
2. Seeds app + core natively on `ubuntu-24.04` and `ubuntu-24.04-arm` (copy the targeted-images seed job, which needs no Hub credentials).
3. Fans out `ci_profiles.py --native` groups x arches (38 jobs) with `max-parallel` around 8, running `ci_classroom.py prepare/qualify/cleanup` plus the new lifecycle harness for the starter set on each arch.
4. Uploads `ci-qualification.json`, lifecycle evidence and the revision-label verification per job.
Expected wall time about 80 to 100 minutes, based on publish run 44798675803.

Fallback without a new workflow: 19 branches `p7/build-test-<group>` each with a single `[build-test-<group>]` commit at the same tree. More noise, same coverage, but the seed is rebuilt 19 times.

## Recommended Plan Breakdown

| Plan | Wave | Content | Requirements |
|------|------|---------|--------------|
| 07-01 Revision binding | 1 | `ARG DS60_SOURCE_REVISION` + LABEL in root and worker Dockerfiles; launcher and `ci_classroom.launcher()` pass sha (or `<sha>-dirty`); `scripts/verify_image_revision.py`; unit tests (fake docker inspect) in tests/test_docker_classroom.py or a new test file; docs/validation.md note | RUN-01 |
| 07-02 Lifecycle harness | 1 | `scripts/check_classroom_lifecycle.py` (guards, snapshots, transitions, cleanup), extend `check_lab_http.py --check-persistence` with progress.json and a learner SQL sentinel; unit tests with the existing fake-docker fixture pattern (tests/test_classroom_launchers.py:230-300) including refusal tests for foreign project names and pre-existing volumes; one real local run on `--starter` from a clean worktree, evidence JSON in `work/` | RUN-02 |
| 07-03 Native both-arch CI qualification | 2 (after 01, 02) | dispatch workflow (or branch-per-group fallback); add lifecycle harness to the python-core job on both arches; push branch, dispatch, collect 38 job results plus revision-label evidence at one sha | RUN-01, RUN-02 |
| 07-04 Evidence and verification | 3 | `07-VERIFICATION.md` ledger: sha, run IDs, per profile/arch result, image IDs and labels, lifecycle step table, explicit exclusions (GPU, k8s, daemon restart) | RUN-01, RUN-02 |

07-01 and 07-02 touch different files except `ci_classroom.py` (07-01 adds build arg; 07-02 may add the harness hook). Assign `ci_classroom.py` edits to 07-01 only, and have 07-02's CI hook land in 07-03, to keep wave 1 conflict-free.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Starting/stopping the classroom | raw `docker compose up/stop` sequences | `./classroom` actions | RUN-02 is about the learner path, including port repair and config-hash logic |
| Persistence probes | new HTTP clients | `check_lab_http.py --check-persistence` (extend it) | Already seeds and verifies pad, evidence and receipts |
| Required check list | a new per-profile list | `ci_classroom.required_checks` | Single source; docs say there is no second hand-maintained list |
| Env sanitising | ad hoc unset | `ci_classroom.clean_environment` | Already strips secrets and DS60_/COMPOSE_ variables |
| Matrix generation | hard-coded group list in YAML | `ci_profiles.py --native` + `docker/ci-profile-groups.json` | Keeps groups in sync with the catalogue |
| Multi-arch | QEMU/buildx | native runners | Policy (ci_classroom.py:189-192) |

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | User volumes `ds60-classroom_{classroom-learning,classroom-runtime,postgres-data}`; Phase 1 volumes `ds60-phase1-browser_*`; total volumes 8.7 GB | None. Harness must never reference them; guard by regex |
| Live service config | Running compose project `ds60-phase1-browser` (55014/55015); `ds60-livetest-pg`; awesome-copilot MCP containers; `tender_feistel`, `condescending_kirch` | None. Do not stop or restart Docker Desktop during this phase |
| OS-registered state | None found (no launchd/systemd units for the classroom) | None |
| Secrets/env vars | Worker token inside `classroom-runtime` volume per project; no Hub credentials needed for Phase 7 | Harness must not print token contents (hash only) |
| Build artifacts | Local tags `ds60sqlpy-lab:1.4.3`, `worker-python-core:1.4.3` (Phase 1, shared), `1.4.0` copies, formatter images; build cache 23.43 GB; `.classroom/ds60-classroom`, `.classroom/ds60-phase1-browser` | Use `1.4.3-p7<sha8>` tags; remove only those afterwards; never prune cache |

## Common Pitfalls

### Pitfall 1: Tag clobbering
**What goes wrong:** `--local-build` with the default tag overwrites `ds60sqlpy-lab:1.4.3`, breaking the user's `ds60-classroom` resume and the Phase 1 stack's repair path.
**How to avoid:** always `--tag 1.4.3-p7<sha8>`; unit test that the harness refuses to run without a suffixed tag.
**Warning signs:** `docker image ls ds60sqlpy-lab` shows `1.4.3` with a new CREATED time.

### Pitfall 2: Same-ref cancellation in targeted-images
**What goes wrong:** a second `[build-test-*]` push to the same branch cancels the first run (targeted-images.yml:11-16).
**How to avoid:** dispatch workflow, or one branch per group.

### Pitfall 3: ci_classroom guards reject local use
**What goes wrong:** project must be `ds60-(ci|pub)-...` (ci_classroom.py:144), version must equal pyproject (146-148), daemon must be native for the requested arch.
**How to avoid:** local harness calls the launcher directly; CI path uses ci_classroom names.

### Pitfall 4: Dirty shared checkout
**What goes wrong:** other agents' uncommitted edits (including `.planning/`, which `.dockerignore` does not exclude) end up in the image; revision label lies.
**How to avoid:** build from `git worktree add <tmp> <sha>`; label `<sha>-dirty` when `git status --porcelain` is non-empty; verifier rejects `-dirty` for qualification.

### Pitfall 5: Memory pressure
**What goes wrong:** about 7.75 GiB engine memory shared with the running Phase 1 stack and MCP containers; heavy workers OOM or the build stalls.
**How to avoid:** starter only locally; one project at a time; heavy groups in CI.

### Pitfall 6: Over-broad cleanup
**What goes wrong:** `down -v` without `-p`, or a mistyped project name, deletes learner volumes.
**How to avoid:** regex guard `^ds60-(p7|ci)-[a-z0-9-]+$`, ownership marker, explicit `-p`, unit test that cleanup refuses `ds60-classroom` and `ds60-phase1-browser`.

### Pitfall 7: Dynamic-port lab recreate looks like data loss
**What goes wrong:** after stop/resume the lab container ID changes because the browser port changed (documented repair). A naive "same container IDs" assertion fails.
**How to avoid:** assert postgres and worker IDs unchanged; allow lab ID change only when `ports.env` changed; always assert volume identity and data.

### Pitfall 8: Fixture reseed masking SQL loss
**What goes wrong:** `--reset-sql` or init reseeds `training.customers`, so a count check passes even if the volume was replaced.
**How to avoid:** sentinel table in a dedicated schema (for example `p7_sentinel`) with a random token, plus `postgres-data` volume CreatedAt comparison.

### Pitfall 9: Treating amd64 app-build success as RUN-01
**What goes wrong:** ordinary pushes qualify amd64 only.
**How to avoid:** RUN-01 evidence must name both arch jobs per group at the same sha.

## Code Examples

Harness skeleton (new code; names of new functions are `[ASSUMED]`; launcher flags and paths are from verified sources cited above):

```python
# scripts/check_classroom_lifecycle.py (sketch)
PROJECT_RE = re.compile(r"^ds60-(p7|ci)-[a-z0-9-]+$")
FORBIDDEN = {"ds60-classroom", "ds60-phase1-browser", "ds60-livetest-pg"}


def guard(project: str) -> None:
    if project in FORBIDDEN or not PROJECT_RE.fullmatch(project):
        raise SystemExit(f"refusing non-disposable project {project!r}")
    for argv in (
        ["volume", "ls", "-q", "--filter", f"label=com.docker.compose.project={project}"],
        ["ps", "-aq", "--filter", f"label=com.docker.compose.project={project}"],
    ):
        if docker(argv).strip():
            raise SystemExit(f"{project} already has resources; pick a new name")


def launch(project: str, tag: str, *extra: str) -> None:
    run(
        [
            "./classroom",
            *extra,
            "--project",
            project,
            "--local-build",
            "--tag",
            tag,
            "--port",
            "0",
            "--database-port",
            "0",
            "--no-browser",
        ],
        timeout=STEP_TIMEOUT,
    )


def snapshot(project: str) -> dict[str, object]:
    # container IDs per service, volume CreatedAt per volume,
    # sha256 of /workspace/.learning/progress.json, sentinel row, token sha256 (never the token)
    ...


STEPS = [
    ("fresh", lambda: launch(P, TAG, "--starter")),
    ("stop", lambda: run(["./classroom", "stop", "--project", P])),
    ("resume", lambda: run(["./classroom", "resume", "--project", P, "--no-browser"])),
    ("restart", lambda: launch(P, TAG)),
    ("recreate", lambda: (compose(P, "down"), launch(P, TAG))),  # no -v
    ("rebuild", lambda: launch(P, TAG, "--rebuild")),
]
# after each non-stop step: check_lab_http.py --url <classroom.url> --confirm-disposable --check-persistence,
# sentinel query, snapshot diff; finally: owner marker check, compose -p P down -v --remove-orphans.
```

Revision label check (verified label key from Dockerfile:12-18; ARG name is `[ASSUMED]`):

```bash
docker image inspect -f '{{ index .Config.Labels "org.opencontainers.image.revision" }}' ds60sqlpy-lab:1.4.3-p7<sha8>
# must print the 40-hex sha passed as --build-arg DS60_SOURCE_REVISION
```

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker Desktop engine | local starter run | ✓ | 29.9.3 arm64 | none needed |
| Docker Compose | launcher | ✓ | 5.7.1 | none needed |
| Disk headroom | local build | partial | images 31.67 GB, cache 23.43 GB used | starter only; budget check |
| amd64 Docker host | RUN-01 amd64 | ✗ locally | n/a | CI `ubuntu-24.04` |
| arm64 native runner | RUN-01 arm64 | ✓ in CI | `ubuntu-24.04-arm` (public repo) | Mac for starter only |
| `gh` CLI with push/dispatch | 07-03 | ✓ | authenticated, repo PUBLIC | n/a |
| Playwright container | optional browser check | ✓ | `mcr.microsoft.com/playwright/python:v1.64.1-noble` (3.46 GB) | skip locally; CI python-core group covers |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** amd64 host (use CI).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (+ xdist, `--dist=loadgroup`) |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `.venv/bin/python -m pytest tests/test_classroom_launchers.py tests/test_docker_classroom.py -n 0 -q` |
| Full suite command | `make test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RUN-01 | Revision label passed and verified; `-dirty` rejected | unit | `pytest tests/test_image_revision.py -q` | ❌ Wave 0 |
| RUN-01 | All 26 profiles x 2 arches pass `required_checks` at one sha | CI integration | `gh workflow run runtime-qualification.yml --ref <branch>`; `gh run view <id> --json jobs` | ❌ (workflow new) |
| RUN-02 | Harness guards refuse foreign/existing projects and unsuffixed tags | unit (fake docker) | `pytest tests/test_classroom_lifecycle.py -q` | ❌ Wave 0 |
| RUN-02 | Data survives fresh/stop/resume/restart/recreate/rebuild | real-Docker integration | `python scripts/check_classroom_lifecycle.py --project ds60-p7-<sha8>-<rand> --tag 1.4.3-p7<sha8> --starter --report work/p7-lifecycle.json` | ❌ |
| RUN-02 | Same on amd64 and arm64 | CI integration | python-core job of the dispatch workflow | ❌ |

### Sampling Rate
- Per task commit: quick run command.
- Per wave merge: `make test` plus `make lint`.
- Phase gate: dispatch run green on both arches at the final sha, local lifecycle evidence attached, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_classroom_lifecycle.py`: guard, snapshot diff and cleanup refusal tests using the fake docker fixture.
- [ ] `tests/test_image_revision.py`: label expectations and verifier.

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | n/a (classroom auth untouched) |
| V3 Session Management | no | n/a |
| V4 Access Control | yes | Ownership marker + project regex; harness may only destroy resources it created |
| V5 Input Validation | yes | Project name regex (launcher `^[a-z0-9][a-z0-9_-]{0,48}$`, harness `^ds60-(p7|ci)-`), tag suffix validation via `valid_image_version` |
| V6 Cryptography | no | Token only hashed for comparison (sha256 via hashlib) |
| V14 Configuration | yes | `clean_environment`; no Hub creds in Phase 7 jobs; artifacts contain hashes not tokens |

| Pattern | STRIDE | Mitigation |
|---------|--------|-----------|
| Cleanup deletes the wrong project's volumes | Tampering/DoS | regex + forbidden list + marker + explicit `-p` |
| Local rebuild retags shared images | Tampering | mandatory `-p7<sha8>` tag suffix |
| Worker token leaked in evidence | Information disclosure | hash only; never `cat` the token into logs |
| Image claims a revision it was not built from | Spoofing | build from clean worktree; `-dirty` marker; verifier |
| Dispatch workflow given Hub write creds | Elevation | no `secrets.DOCKERHUB_*` in the new workflow; `permissions: contents: read` |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ARG name `DS60_SOURCE_REVISION` and LABEL placement in final stage keep build cache effective | Q2 | Slower builds; rename is trivial |
| A2 | New dispatch workflow wall time about 80 to 100 min | Q5 | Longer CI wait only |
| A3 | Local starter rebuild with warm cache fits within 45 min | Q5 | Raise timeout or move to CI |
| A4 | A sentinel schema `p7_sentinel` does not collide with course SQL | Pitfall 8 | Rename schema |
| A5 | Docker Desktop restart is out of scope for this shared host | Q4 gap 8 | Record as documented manual exclusion |
| A6 | New script/workflow/test file names | Plans | Cosmetic |

## Open Questions (resolved with recommendations)

1. **New dispatch workflow or 19 marker branches?** Recommend the dispatch workflow: one sha, one run ID, one seed per arch. Fallback to branches only if workflow review is blocked.
2. **Should GPU profiles count as "supported"?** No. They are excluded from release (docker_release.py:175) and from CI groups; record as explicit exclusion with that citation.
3. **Extend ci_classroom.py or add a separate script?** Separate `check_classroom_lifecycle.py` for local use (ci_classroom guards are CI-specific), invoked from CI after `ci_classroom qualify`, under the ci project name.
4. **Does qualifying require a publish?** No. Phase 7 stays Hub-free; Phase 10 publishes the sha Phase 7 qualified (or re-qualifies through the publish workflow, which already repeats these checks).
5. **Which sha?** The tip of the branch after 07-01 and 07-02 land and after Phases 3 to 6 content commits, so Phase 8 and 10 inherit the same revision. If content changes later, rerun 07-03 (about 90 minutes).
6. **Kubernetes images?** Out of scope; not part of the release set.

## Sources

### Primary (HIGH)
- Repo files read this session: docker/classroom-images.tsv, docker/ci-profile-groups.json, docker/ci-scientific-projects.json, Dockerfile, compose.yaml, compose.classroom.yaml, compose.modules.yaml, .dockerignore, Makefile, scripts/classroom.sh, scripts/classroom_images.sh, scripts/ci_classroom.py, scripts/ci_profiles.py, scripts/ci_targeted_images.py, scripts/docker_release.py, scripts/check_lab_http.py, scripts/ci_scientific_projects.py, .github/workflows/{ci,app-build,targeted-images,publish-images,kubernetes,verify-published-images,audit-published-release}.yml, tests/test_classroom_launchers.py, tests/test_docker_classroom.py, docs/one-command-classroom.md, docs/validation.md, pyproject.toml.
- `gh run view` 44798675803 (publish 1.4.3), 45301514511 (app-build), 41124262125 (targeted).
- Read-only `docker version/info/ps/image ls/system df/volume ls/compose ls`.

### Secondary (MEDIUM)
- Phase 1 artifacts and `~/.cache/ds60sqlpy/run-browser.sh`.

### Tertiary (LOW)
- None used for factual claims.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, all tooling exists in repo/host.
- Architecture: MEDIUM, harness is new but composed of verified primitives.
- Pitfalls: HIGH, each traced to a specific line or observed host state.

**Research date:** 2026-11-21
**Valid until:** 2026-12-05 (CI workflows and launcher change often)

## Five-line summary

1. Release set is 26 profiles (app + 25 ordinary, GPU excluded at docker_release.py:175) x amd64/arm64, built only on native runners; ordinary pushes qualify amd64 only.
2. Local and ordinary-CI images carry an empty `org.opencontainers.image.revision`; add a build-arg label plus a verifier and build from a clean worktree.
3. Real-Docker persistence proof covers only `down` + `--no-build` in CI; stop/resume, restart, `--rebuild`, progress.json and learner SQL objects are unproven.
4. Harness: `ds60-p7-<sha8>-<rand>` project, `--tag 1.4.3-p7<sha8>`, ports 0, owner marker, `down -v` only on its own project; starter locally, heavy groups in CI.
5. Plans: 07-01 revision binding and 07-02 lifecycle harness (wave 1), 07-03 both-arch dispatch qualification (wave 2), 07-04 evidence ledger (wave 3).
