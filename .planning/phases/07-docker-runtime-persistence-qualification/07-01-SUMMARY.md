---
phase: 07-docker-runtime-persistence-qualification
plan: 01
subsystem: docker-images
status: complete
requirements: [RUN-01]
tags: [docker, oci-labels, provenance, release]
requires: []
provides:
  - OCI revision/version/source labels on app and all 22 worker Dockerfiles via build args
  - Launcher computes the source revision and passes it on every local build
  - scripts/verify_image_revision.py (JSON report, rejects empty and -dirty labels)
  - docker_release.inspected_image refuses a revision label that differs from Context.revision
affects: [07-03, 08-03, 08-04, 10]
key-files:
  created:
    - scripts/verify_image_revision.py
    - tests/test_image_revision.py
  modified:
    - Dockerfile
    - docker/workers/Dockerfile.* (22 files)
    - .dockerignore
    - scripts/classroom.sh
    - scripts/docker_release.py
    - tests/test_docker_release.py
    - docs/validation.md
decisions:
  - Revision ARG and LABEL are the last instructions of each final stage so a new commit reuses every earlier cached layer.
  - The launcher labels a build only when the directory is its own git top level; a parent repository yields an empty label.
  - Untracked, non-ignored files count as dirty (git status --porcelain), because they would enter the build context.
commits: 0
plan_head_before: 5ad22de5443ca3567e221032de0580ee224f4621
plan_head_after: 5ad22de5443ca3567e221032de0580ee224f4621
actuals:
  tasks: 3
  commits: 0
---

# Phase 7 Plan 01: Image revision binding Summary

Every locally built classroom image now carries `org.opencontainers.image.revision`
set from `--build-arg DS60_SOURCE_REVISION` that `./classroom` computes (40-hex sha,
`<sha>-dirty`, or empty), workers also carry version and source labels, and a
verifier plus a release-staging gate refuse anything that is not the exact clean commit.

Commits: none by this agent (orchestrator rule: the shared tree is never staged or
committed by executors). `commits: 0` is expected; all changes are uncommitted in the
working tree for the orchestrator to commit.

## What was done

Task 1 (tracer, app and python-core)
- `Dockerfile`: removed the literal empty `org.opencontainers.image.revision=""` from the
  top LABEL (kept the literal `version="1.4.3"` that `docker_release.py` gates); appended
  `ARG DS60_SOURCE_REVISION=""` and `LABEL org.opencontainers.image.revision=...` after
  `CMD`, as the final instructions.
- `docker/workers/Dockerfile.python-core`: appended the worker trailer
  (`ARG DS60_SOURCE_REVISION`, `ARG DS60_RELEASE_VERSION`, one LABEL with revision,
  version and source URL).
- `scripts/classroom.sh`: new `image_source_revision` helper (git optional, physical
  top-level must equal `repo_dir`, `-dirty` on any porcelain output, never fails the
  launcher); `build_release_version` read with awk from `pyproject.toml` (named to avoid
  clobbering `release_version` from `classroom_images.sh`); `revision_args` added to both
  the python-core `docker build` and `compose build` (placed before the service name);
  prints `Building from source revision <value|unknown>.` only for local builds with
  work to do. Empty-array expansion is bash 3.2 and `set -u` safe. Compose YAML untouched.
- `scripts/verify_image_revision.py`: CLI per plan (`--revision`, `--tag`, repeatable
  `--profile` with `app` always included, `--architecture`, `--report`), resolves
  repositories from `docker/classroom-images.tsv`, rejects unknown and GPU profiles,
  one `docker image inspect --format '{{json .}}'` per image via argv list, report
  holds only labels and IDs. mypy `--strict` clean. Runner is injectable for tests.
- `tests/test_image_revision.py`: verifier pass/fail cases for every field, bad
  revision refused before Docker, arch mapping; launcher tests reuse the `launcher`
  fixture (no edits to that file): empty revision under the parent repo, then
  `git init`+commit gives the sha, then editing a tracked file gives `<sha>-dirty`;
  `DS60_RELEASE_VERSION` asserted on every build row.

Task 2 (all workers, .dockerignore)
- Structural tests written first and observed failing: 43 failed (21 + 21 trailer
  tests and the `.planning` test) while all Task 1 tests passed.
- Appended the identical trailer to the 21 remaining worker Dockerfiles at end of file
  (final stage for multi-stage java, node, spark, julia). No base image, ARG default,
  RUN or COPY line changed, so Phase 8 base-image edits at the top of each file will
  not conflict.
- `.dockerignore`: added `.planning` with a comment next to `work`.

Task 3 (release gate, docs)
- `scripts/docker_release.py::inspected_image`: after the seed version gate, raises
  `ReleaseError("Local image revision label must match the release revision")` for any
  profile whose `Config.Labels[REVISION]` differs from `context.revision`.
- `tests/test_docker_release.py`: both label fixtures carry `release.REVISION:
  context.revision`; new parametrized test (app, python-core, java21 x empty, other
  sha, missing, `-dirty`) proves refusal and that the matching label passes.
- `docs/validation.md`: new subsection "Prove which commit an image came from" inside
  "Exercise the Docker product on disposable data".

## Verification (real results)

- `pytest -n 0 --basetemp=work/test-tmp-07-01 tests/test_image_revision.py tests/test_classroom_launchers.py tests/test_docker_classroom.py tests/test_docker_release.py -q`: 355 passed in 386s.
- After formatting: `tests/test_image_revision.py tests/test_docker_release.py`: 128 passed; `tests/test_image_revision.py` collects 67 tests.
- `ruff check src scripts tests`: All checks passed.
- `ruff format --check` on the four Python files this plan touched: clean.
- `mypy --strict scripts/verify_image_revision.py`: no issues.
- `set -a; . ./.env; set +a; ./scripts/lint-repo --language shell --language docker`: Lint checks passed (37 shell, 48 docker files).
- Trailer grep over `docker/workers/Dockerfile.*` and exact `.planning` line in `.dockerignore`: ok.
- Em/en dash scan on all edited files: none.
- Tracer build (arm64 host): `bash classroom build --project ds60-p7-84931f56-fe9814 --starter --local-build --tag 1.4.3-p784931f56 --no-browser` from a clean scratch clone, exit 0; log printed `Building from source revision 84931f56927bf8624e1b3eacb3568993c48ddb2f.` Afterward the project had zero containers, volumes and networks.
- `scripts/verify_image_revision.py --revision 84931f56927bf8624e1b3eacb3568993c48ddb2f --tag 1.4.3-p784931f56 --report work/p7-0701-tracer.json`: exit 0, `"passed": true` for both:
  - app `ds60sqlpy-lab:1.4.3-p784931f56` image ID `sha256:e139cee65a35472be101304852a3e646c1f043fa6fd69776af1fe577284b7a62`
  - python-core `ds60sqlpy-worker-python-core:1.4.3-p784931f56` image ID `sha256:e013e344a1375446702cbb0bbb66b219aeffa2715cac9b911d47e905dc753850`
  - both labels: revision = that sha, version 1.4.3, source https://github.com/sadatnfs/ds60sqlpy
- Negative real-image check: verifier against shared `1.4.3` tags exits 1 with "revision label is empty or missing" for both (report `work/07-01/negative-shared-tag.json`).
- Cleanup: removed exactly the two `-p784931f56` tags and the scratch clone. Shared `ds60sqlpy-lab:1.4.3` (42a928f2fff8) and `ds60sqlpy-worker-python-core:1.4.3` (275fcdd845d0) unchanged; no protected container touched.

## Deviations from Plan

1. [Rule 3 - Blocking] Tracer source. The plan's tracer builds from `git worktree add` of HEAD after Task 1 is committed. Executors may not commit, so HEAD (5ad22de5) does not contain these changes. Instead I made an isolated `git clone --shared` under `work/`, copied this plan's 30 files into it, and committed there (scratch identity, separate repository; the shared index, refs and worktree list were not touched). Its scratch sha `84931f56...` is what the images were labeled with and verified against. The proof is structurally identical (clean tree, own git top level), but the sha is not a commit on `main`. `.env` was copied into the clone (gitignored there) to reach the package proxy.
2. Basetemp `work/test-tmp-07-01` instead of `work/test-tmp` (orchestrator rule).
3. `lint-repo` was run for the `shell` and `docker` languages only (the files this plan touches), not the full catalog.

## Pre-existing issues not caused by this plan (not fixed)

- `mypy src`: `src/ds60sqlpy/walkthroughs.py:191` assignment error; that file is untracked and owned by another agent.
- `ruff format --check src scripts tests`: `tests/test_module_api.py` would be reformatted; not in this plan.

## Notes for 07-03

- Qualification must label images with a real commit: build from a clean CI checkout of `github.sha` (or a clean worktree locally); the launcher computes the revision itself, so `scripts/ci_classroom.py` needs no change.
- Run `python scripts/verify_image_revision.py --revision "$GITHUB_SHA" --tag <tag> --profile <each profile in the group>` after the build; `--architecture` can be omitted on native runners.
- Images built directly with `docker compose build` (bypassing `./classroom`) get empty revision and, for workers, an empty version label because the trailer overrides the inherited one. `docker_release.inspected_image` now refuses any image whose revision label is not the release revision, so publication must stage images built through the launcher at that exact commit.
- The worker version label also overrides the app's literal version in python-core; launcher builds set it to the pyproject version, which keeps the existing seed version gate passing.

## Known Stubs

None.

## Threat Flags

None. No new network surface; the verifier only runs local `docker info` and `docker image inspect`.

## Self-Check: PASSED

- Files exist: scripts/verify_image_revision.py, tests/test_image_revision.py, work/p7-0701-tracer.json.
- No commits claimed (commits: 0 by design under orchestrator rules).
