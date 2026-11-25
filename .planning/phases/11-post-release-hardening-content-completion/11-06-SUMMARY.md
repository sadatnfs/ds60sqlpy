---
phase: 11-post-release-hardening-content-completion
plan: 06
subsystem: content-validation
status: complete
requirements: [HARD-03]
requirements-completed: [HARD-03]
tags: [guides, code-samples, ci, validation, fence-annotations]
requires: [11-01]
provides:
  - scripts/check_guide_examples.py, which classifies and runs or statically checks every companion guide's fenced blocks
  - fence annotations (fragment, external, expect-error, isolated, prelude=, profile=) for blocks that are not standalone programs
  - CI lanes for host, PostgreSQL, advanced Python and every Docker worker group
  - a guide_examples ledger entry for all 40 tracks that names the executed scope
affects: [11-07, 11-08]
key-files:
  created:
    - scripts/check_guide_examples.py
    - src/ds60sqlpy/snippet_shape.py
    - tests/test_check_guide_examples.py
    - .planning/phases/11-post-release-hardening-content-completion/11-06-SUMMARY.md
  modified:
    - src/ds60sqlpy/exercises.py
    - src/ds60sqlpy/execution.py
    - src/ds60sqlpy/lab.py
    - scripts/check_track_qualification.py
    - scripts/format_inline_code.py
    - ".github/workflows/{ci,app-build,kubernetes,relock-python}.yml"
    - curriculum/track-qualification.json
    - curriculum/coverage-matrix.json
    - "docs/{content-authoring,validation,track-qualification,coverage-matrix,lesson-depth-report}.md"
    - "tests/{test_ci_contract,test_execution,test_format_inline_code,test_learning_lab,test_track_qualification}.py"
    - "courses/**/guides/*.md (234 guide files)"
decisions:
  - The harness splits each guide with the reader's own fence rules, so it checks the same blocks a learner sees. Blocks that are not standalone programs are marked with a fence annotation instead of being skipped silently.
  - A block whose optional runtime is absent is reported as skipped, never as passed, and a run must have 0 failed blocks.
  - SQL blocks run as one cumulative script per guide in a disposable Postgres database. A failing block that is a verbatim excerpt of its lesson file passes as an excerpt.
  - Worker-image runs use no network, a read-only root, dropped capabilities and a non-root user. Python, R and Julia blocks run cumulatively per guide; compiled and scripting languages run one complete program per block.
  - The snippet-shape helpers moved to a stdlib-only module, src/ds60sqlpy/snippet_shape.py, shared by the classroom pad and the harness.
commits: [02e6261c, f26968d1, b160d82b]
actuals:
  tasks: 4
  commits: 3
completed: 2026-11-24
---

# Phase 11 Plan 06: execute guide code samples Summary

Companion guide code blocks are now run in their own runtimes or statically checked
(HARD-03). Fragments carry an explicit fence annotation instead of being skipped silently.
`scripts/check_guide_examples.py` (1,874 lines) covers every guide in
`curriculum/coverage-matrix.json`, and CI runs it in four lanes. The ledger for all 40 tracks
now names what it executes. Commit 02e6261c touched 387 files (3 added, 384 modified;
3,573 insertions and 994 deletions). Of those, 234 are guide markdown files and 46 are
regenerated lesson and reference pages.

## Harness

The checker classifies each fenced block and handles it by class:

| Class | Handling |
| --- | --- |
| Documentation | Recorded only |
| Static host checks | `bash -n`, JSON, YAML and XML parsing |
| SQL | Cumulative script per guide in a disposable Postgres database |
| Worker languages | Run inside the track's worker image |
| Stan models | `stanc` |

- Fence annotations, documented in `docs/content-authoring.md` (+29): `fragment`, `external`,
  `expect-error`, `isolated`, `prelude=<path>` and `profile=<name>`.
- Main options: `--confirm-disposable` (required), `--list-only`, `--profiles`, `--guides`,
  `--psql`, `--database-container`, `--advanced-python`, `--track-image`, `--image-template`,
  `--bash`, `--jobs` and `--report`.
- An `expect-error` block fails if it succeeds.
- `docs/validation.md` (+67) adds a "Guide example execution" section. A local `--profiles all`
  run with every runtime available remains the release gate.

## CI lanes

- `ci.yml` core job (Python 3.12): `--profiles host`.
- `ci.yml` PostgreSQL job: `--profiles postgres --psql 'psql -X -h localhost -U ds60'`. It
  uploads `guide-sql.json`.
- `ci.yml` advanced imports job: `--profiles python-advanced --advanced-python .venv/bin/python`.
- `app-build.yml` docker job:
  - Runs `--profiles "$CI_PROFILES" --image-template 'ds60sqlpy-worker-{profile}:{version}'`
    with `--jobs 2 --max-minutes 60` for each worker group, and uploads
    `work/guide-examples-<group>.json`.
  - Follow-up b160d82b: this step first ran under the bare runner Python and failed with
    `ModuleNotFoundError: pygments` in all 9 docker groups. The job now installs setup-uv
    v10.4.0, runs `uv sync --frozen`, and invokes the checker with `uv run --no-sync`.
    `tests/test_ci_contract.py` pins that order.

## Content and ledger

- Guide files fixed or annotated, by course: python-web 69, apache-data-platforms 37,
  tmb-modeling 25, web-development 19, advanced-spark-modeling 18, python/professional 17, and
  smaller counts elsewhere. The guides gained 130 `fragment`, 69 `isolated`, 27 `prelude=`,
  24 `external`, 15 `profile=` and 5 `expect-error` annotations. Authoring sources such as the
  apache and spark-deployment chapters were updated to match.
- `curriculum/track-qualification.json`: every track's `runtime.guide_examples` text now
  states the executed scope. 32 tracks cite `scripts/check_guide_examples.py`, 5 have no
  ordinary executable reference, and 3 are covered by the core course checks.
  `docs/track-qualification.md` updates the field definition.
- `curriculum/coverage-matrix.json`: example metrics were updated for 246 lessons.

## Related changes in these commits

- `src/ds60sqlpy/execution.py` renames `trusted_setup` to `solution_setup`, clearing a CodeQL
  finding from plan 11-04.
- f26968d1 rewrites one C function-signature regex with lookaheads. This removes exponential
  backtracking (CodeQL `py/redos` alert #2). The commit reports unchanged behavior on all
  100,596 guide lines that contain a call.
- Dependabot's `astral-sh/setup-uv` v10.3.3 to v10.4.0 bump was folded into `ci.yml`,
  `app-build.yml`, `kubernetes.yml` and `relock-python.yml`.

## Verification

- Classification, annotations, skipped-versus-passed reporting and the excerpt rule: covered by
  `tests/test_check_guide_examples.py` (15 tests).
- Shared snippet helpers and the renamed parameter: covered by `tests/test_execution.py`,
  `tests/test_learning_lab.py` and `tests/test_format_inline_code.py`.
- Ledger wording: covered by `tests/test_track_qualification.py` and
  `scripts/check_track_qualification.py`.
- Docker lane ordering: covered by `tests/test_ci_contract.py` (b160d82b).
- Harness passing locally for Python and in CI for the worker groups: the lanes exist, but these
  commits record no run result. The release-gate run is verified in plan 11-08.

## Deviations

- **CI fix after the plan commit.** The Docker lane needed b160d82b to run the checker in the
  locked uv environment.
- **CodeQL fixes from plan 11-04 landed here** (the `solution_setup` rename in 02e6261c and the
  regex fix in f26968d1).
- **Folded Dependabot bump.** The setup-uv bump was folded into 02e6261c instead of merging its
  separate Dependabot PR.
- **New helper module.** `src/ds60sqlpy/snippet_shape.py` was extracted from `exercises.py` so
  the harness and the classroom pad share one definition of a standalone snippet. The plan did
  not name this module.

## Self-Check: PASSED

Tasks 1 to 4 map to 02e6261c, with the CI follow-up in b160d82b and the regex fix in f26968d1.
The recorded harness run is deferred to plan 11-08.
