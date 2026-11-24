---
phase: 07-docker-runtime-persistence-qualification
plan: 03
subsystem: ci-runtime-qualification
status: complete
requirements: [RUN-01, RUN-02]
tags: [ci, docker, native-arm64, qualification, lifecycle]
requires: [07-01, 07-02]
provides:
  - .github/workflows/runtime-qualification.yml (dispatch-only, 19 groups x 2 native architectures plus 2 lifecycle jobs)
  - tests/test_runtime_qualification_workflow.py (14 contract tests)
  - docs/validation.md runtime qualification and local lifecycle sections
affects: [07-04, 08-04]
key-files:
  created:
    - .github/workflows/runtime-qualification.yml
    - tests/test_runtime_qualification_workflow.py
  modified:
    - docs/validation.md
    - tests/test_ci_contract.py (runtime-qualification.yml branch, applied in 09f0c0cc)
decisions:
  - The revision step verifies python-core plus the group profiles, because the launcher always builds python-core.
  - The group filter is validated in Python against known group IDs; unknown or hostile tokens fail the selection job.
  - Cleanup is not asserted to be the final step, so Phase 8 can append an image scan step (cleanup keeps local images).
  - Lifecycle uploads the redacted work/p7-logs/ directory as well as the JSON report.
commits: 2
actuals:
  tasks: 3
  commits: 2
completed: 2026-11-24
---

# Phase 7 Plan 03: Two-architecture runtime qualification workflow Summary

A manual `runtime-qualification.yml` workflow builds every ordinary profile group through
`./classroom` on native amd64 and arm64 runners, proves each image's revision label equals
`$GITHUB_SHA`, qualifies the group, and runs the full 07-02 lifecycle harness (with a real
update rebuild) on both architectures. A 14-test contract pins its behavior.

All three tasks are done. The executor made no commits (orchestrator rules); the orchestrator
committed the workflow, test and contract branch in `09f0c0cc` and adjusted the workflow in
`a2958a3a`, then pushed and dispatched it (Task 3 below).

## What was done

Task 1 (tracer): workflow and contract test (test written first: 14 failed, then 14 passed)
- `matrix` job (`ubuntu-24.04`): `GROUPS_FILTER: ${{ inputs.groups }}` is passed via `env:`
  only. The step runs `scripts/ci_profiles.py --native`, filters rows in Python, rejects unknown
  IDs, and writes `matrix` and `version` (from pyproject via tomllib).
- `groups` job: `runs-on: ${{ matrix.runner }}`, timeout 180, fail-fast false, max-parallel 8.
  `CI_PROJECT=ds60-ci-<project_group>-<architecture>-<run_id>-<attempt>` (max 48 characters,
  checked in the test against both the driver regex and the 49-character limit). The steps are:
  1. `ci_classroom.py prepare`
  2. `verify_image_revision.py --revision "$GITHUB_SHA" --tag "$RELEASE_VERSION" --architecture "$CI_ARCH" --report work/image-revision.json` with `--profile python-core` plus one `--profile` per group profile (via `read -ra`)
  3. `qualify`
  4. `diagnostics` on `failure()`
  5. upload `runtime-<arch>-<group>` with `always()` and 14-day retention
  6. `cleanup` with `always()`
- `lifecycle` job: two native rows, timeout 150, checkout with `fetch-depth: 2`. It runs `check_classroom_lifecycle.py --project "ds60-p7-<arch>-<run_id>-<attempt>" --base HEAD~1 --target HEAD --architecture <arch> --report work/p7-lifecycle-<arch>.json`, with no `--seed-images` and no `--steps`, so all eight transitions run, including a real update rebuild. It then uploads `lifecycle-<arch>` (`work/p7-lifecycle-*.json`, `work/p7-logs/`). It does not depend on `groups`.
- Workflow security: `permissions: contents: read`, no `secrets.`, actions pinned by SHA (same pins as `app-build.yml`), `persist-credentials: false`. The workflow has no qemu, binfmt, `--platform` or prune. Concurrency `runtime-qualification-${{ github.ref }}` with `cancel-in-progress: false`.
- What the contract test covers:
  - triggers, permissions, pins, checkouts, native runners and no emulation
  - step order, artifact names and paths, project name limits, lifecycle arguments, and that inputs stay in `env:` only
  - it runs the real selection step in bash: empty filter gives all 38 rows, `python-core` gives 2 rows, and hostile or unknown values fail with no output

Task 2: `docs/validation.md`
- New sections "Qualify both architectures at one commit" and "Exercise lifecycle transitions locally" after the 07-01 revision subsection.
- They cover what runs, smoke and full dispatch commands, the rule that the workflow must already be on main, `gh run download`, artifact contents, and the exclusions with reasons (GPU, Kubernetes, daemon restarts).
- The lifecycle section covers the harness command, the eight transitions, the ownership marker and the protected snapshot.

## Verification (real results)

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-07-03 -q tests/test_runtime_qualification_workflow.py tests/test_ci_contract.py` | 1 failed, 26 passed. The failure is `test_ci_contract.py::test_release_jobs_target_linux_containers_and_contributor_tooling`: it requires every unlisted workflow to use only `ubuntu-latest` (see Deviations) |
| Same tests with `work/07-03/test_ci_contract.patch` applied to a scratch copy | 27 passed |
| `git apply --check work/07-03/test_ci_contract.patch` | applies cleanly to the current file |
| `pytest tests/test_runtime_qualification_workflow.py` alone | 14 passed (RED before the workflow existed: 14 failed) |
| `ci_profiles.py --native` 38 rows / 2 runners check (Task 1 verify 3) | ok |
| `yaml.safe_load` on the workflow | ok |
| `docker run rhysd/actionlint:1.7.7` on the workflow (shellcheck bundled) | exit 0, no findings; image removed afterwards |
| `ruff check` / `ruff format --check` on the new test | All checks passed / already formatted |
| Task 2 docs grep + dash check | ok |
| `set -a; . ./.env; set +a; ./scripts/lint-repo` | exit 1. Python, docker, shell and all other languages passed. The only error is `scripts/check_classroom_ui.mjs:1334: javascript syntax error`; that file is modified by another agent and this plan does not touch it |
| Dash scan (perl) on the workflow, test, docs and patch | none |

## Deviations

1. **`tests/test_ci_contract.py` not edited (orchestrator instruction: 08-02 owns it).**
   - The existing test fails for any new workflow not on `ubuntu-latest`, so `runtime-qualification.yml` makes it fail until a branch is added.
   - A minimal 8-line `elif path.name == "runtime-qualification.yml"` branch is prepared in `work/07-03/test_ci_contract.patch`. It was validated on a scratch copy (27 passed) and checked with `git apply --check`.
   - The orchestrator (or 08-02) must apply it before committing Task 1. Otherwise the CI `ci.yml` test job will fail on main.
2. **Revision verification also checks python-core** (Rule 2): `scripts/classroom.sh` always adds python-core to the profile set, so it is part of each group's build.
3. **Cleanup is not required to be the last step.** This lets 08-04 append a scan step; the comment in the groups job marks the spot.
4. **Plan basetemp `work/test-tmp` replaced** by `work/test-tmp-07-03` (orchestrator rule); deleted afterwards.

## Task 3: push and dispatch (orchestrator)

- `tests/test_ci_contract.py` gained the `runtime-qualification.yml` branch in `09f0c0cc` (line 211), so `ci.yml` stays green.
- Smoke dispatch 45353094698 at `3a7cf526` (`groups=python-core`) failed in both python-core runtime jobs: the host side `scripts/check_module_references.py` imported `pygments`, which the hosted runner Python lacks. Lifecycle was not the cause.
- `3e228c34` made the host reference checker free of third-party imports. Smoke dispatch 45356808560 at `3e228c34` then passed every job: `Select native qualification groups`, `Runtime amd64 (python-core)`, `Runtime arm64 (python-core)`, `Lifecycle amd64` and `Lifecycle arm64` (build mode, all eight steps including the real update).
- Full dispatch 45367221536 at `6f4bf87c` was cancelled and superseded by a dispatch at the final Phase 9 commit.
- Full dispatch 45381453466 targets the pushed SHA `46dc32fc41badbe5128ceeb145740b5bcdc32f89` (all 38 group rows and both lifecycle rows). Its artifacts go to `work/p7-evidence/45381453466/`, and 07-04 turns them into `07-VERIFICATION.md`.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model (T-07-11 and T-07-12 are mitigated and tested).
