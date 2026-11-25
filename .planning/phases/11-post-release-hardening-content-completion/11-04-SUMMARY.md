---
phase: 11-post-release-hardening-content-completion
plan: 04
subsystem: security
status: complete
requirements: [HARD-01]
requirements-completed: [HARD-01]
tags: [security, cve-policy, codeql, dependabot, docker, locks]
requires: []
provides:
  - an App image that no longer ships repository Dockerfiles, so its scan reports no DS-0002 findings
  - CodeQL code scanning on every push and pull request to main and weekly
  - grouped, security-only Dependabot updates for uv, pip, npm and gomod manifests
  - relocked Python, Node and Go dependencies with every fixable alert's patched version
  - docker/cve-policy.json reduced from 276 to 229 entries, all still pending-owner
affects: [11-03, 11-05, 11-08]
key-files:
  created:
    - .github/codeql/codeql-config.yml
    - .github/workflows/codeql.yml
    - .planning/phases/11-post-release-hardening-content-completion/11-04-SUMMARY.md
  modified:
    - .dockerignore
    - docker/cve-policy.json
    - docker/workers/Dockerfile.php
    - compose.modules.yaml
    - .github/dependabot.yml
    - .github/workflows/relock-python.yml
    - pyproject.toml
    - uv.lock
    - "courses/llm-applied/fixtures/pretrained/{pyproject.toml,requirements.amd64.lock,requirements.arm64.lock}"
    - "docker/workers/gpu/requirements-pytorch-cuda.{in,lock}"
    - courses/go/fixtures/client-go-project/go.mod
    - docker/formatting/package.json
    - tests/test_ci_contract.py
    - tests/test_advanced_imports.py
decisions:
  - CodeQL scans src, scripts, docker, packages and .github only. Course content is excluded because the security lessons contain deliberately vulnerable snippets for learners.
  - The PHP worker copies the patched upstream CPython 3.12.16 from the pinned python:3.12.16-slim-trixie image instead of installing Debian python3, which removes the python3.13 package backlog from that image.
  - Intel macOS no longer installs torch on the host (the 2.2.2, numpy<2 and torchvision 0.17.2 rows are gone); those learners use the Docker worker, so the patched torch line applies everywhere else.
  - Dependabot security updates are grouped into one pull request per ecosystem, and open-pull-requests-limit 0 turns version updates off. Before this, each alert opened its own PR and every push to main rebased all of them, which queued dozens of CI runs.
  - No pending-owner CVE exception was approved, and no Dependabot alert was dismissed.
commits: [930d28de, dd004be5, bb9176f5, 4f213632, 92c9ebdb, 0a868168]
actuals:
  tasks: 4
  commits: 6
completed: 2026-11-24
---

# Phase 11 Plan 04: shrink the security exception surface and add code scanning Summary

The App image no longer carries repository Dockerfiles, CodeQL scans every push, and the
dependency locks were refreshed to the patched versions. The CVE policy also shrank from 276 to
229 entries, and none was approved on the owner's behalf (HARD-01). One follow-up stays open:
77 Dependabot alerts still show as open against manifests that main has already fixed. Plan
11-08 verifies them.

## Image findings (930d28de)

- `.dockerignore` excludes `/Dockerfile`, `docker/**/Dockerfile` and `docker/**/Dockerfile.*`,
  so the image recipes no longer ship under `/opt/course`. The App never builds or runs them.
  Learner Dockerfiles under `courses/`, `examples/` and `packages/` still ship.
- `docker/workers/Dockerfile.php` copies CPython 3.12.16 from the pinned
  `python:3.12.16-slim-trixie` image, removes site-packages and ensurepip, and smoke-imports
  `json`, `sqlite3`, `ssl` and `http.server`. `compose.modules.yaml` passes `DS60_PYTHON_IMAGE`.
- `docker/cve-policy.json` changes:

| Change | Entries |
| --- | --- |
| Before (249 vulnerability, 27 misconfiguration) | 276 |
| DS-0002 entries for `/opt/course` Dockerfiles removed | -27 |
| Debian `python3.13`, `python3.13-minimal`, `libpython3.13-stdlib`, `libpython3.13-minimal` entries removed (5 CVEs each) | -20 |
| After (vulnerability only) | 229 |

`php-cli` was dropped from 5 more entries' image lists. `r-statistics` was added to the 137
`linux-libc-dev` kernel-header entries (plan 11-03). All 229 remaining entries keep reviewer
`pending-owner` and expire on 2026-12-23 (60 entries) or 2026-12-24 (169 entries).

## Code scanning (930d28de)

`.github/workflows/codeql.yml` runs on push and pull request to `main`, weekly
(`17 6 * * 1`) and on dispatch. It covers `actions`, `javascript-typescript` and `python` with
`build-mode: none` and `security-extended` queries, using `actions/checkout` v7.0.1 and
`github/codeql-action` v4.39.5 pinned by SHA. `tests/test_ci_contract.py` now accepts SHA-pinned
sub-path actions such as `github/codeql-action/init`. The CodeQL findings on this code were
fixed in plan 11-06 commits: the `trusted_setup` parameter, which CodeQL read as a secret, was
renamed `solution_setup` (02e6261c), and a C-signature regex in
`scripts/check_guide_examples.py` no longer backtracks exponentially (f26968d1, `py/redos`
alert #2). CodeQL shows 0 open alerts.

## Dependencies (dd004be5, bb9176f5, 4f213632)

- `pyproject.toml` deep-learning extra: torch 2.14.1 and torchvision 0.29.1 on arm64 macOS,
  torch>=2.14 and torchvision>=0.29 elsewhere. The Intel macOS rows are removed.
- `uv.lock`: accelerate 1.16.0, transformers 5.24.1, torch 2.15.0, cryptography 50.0.2,
  setuptools 84.2.1 and urllib3 2.8.0.
- Pretrained fixture: torch 2.15.0+cpu, transformers 5.23.0, trl 1.18.0, peft 0.21.3,
  datasets 5.2.0, accelerate 1.16.0, safetensors 0.8.0 and huggingface-hub 2.4.0. The amd64 and
  arm64 locks, guides llm-applied-003, 014 and 021, and their solutions were updated to match.
- CUDA worker: `requirements-pytorch-cuda.in` pins torch==2.15.0, and the lock was regenerated.
- Go fixture: golang.org/x/net v0.47.0 to v0.55.0, with x/sys v0.45.0, x/term v0.43.0 and
  x/text v0.37.0.
- `docker/formatting/package.json`: typescript-eslint 8.73.0, plus lodash and lodash-es 4.18.1
  overrides.
- Spark build locks: setuptools 84.2.1, and `wheel` was removed.
- `.github/workflows/relock-python.yml` is now "Relock dependencies", with a target of
  `uv-lock`, `pretrained` or `go-fixture`.
- `.github/dependabot.yml` adds grouped security-update entries for uv (`/`), pip (pretrained
  fixture, `docker/workers/gpu`, `packages/spark-tmbad/tooling`), npm (`/docker/formatting`) and
  gomod (Go fixture). 17 open Dependabot PRs were closed as superseded by the relock.
- 92c9ebdb annotates a loop variable in `tests/test_ci_hub_release_audit.py` for mypy 2.3 on
  Python 3.11. 0a868168 applies ruff formatting to the relocked llm-applied sources.

## Verification

- No DS-0002 entries remain and the policy shrank: shown by the `docker/cve-policy.json` diff in
  930d28de (27 misconfiguration entries to 0, 276 to 229 entries). The App scan itself runs in
  the release gate in plan 11-08.
- CodeQL workflow pins: covered by `tests/test_ci_contract.py`.
- Deep-learning extra pins: covered by
  `test_deep_learning_extra_pins_patched_wheels_and_skips_intel_macs` in
  `tests/test_advanced_imports.py`.
- Dependabot alerts at close: 77 remain open (73 on `uv.lock`, 3 on
  `docker/workers/gpu/requirements-pytorch-cuda.in` for torch, 1 on the Go fixture `go.mod` for
  golang.org/x/net < 0.55.0), but main already pins every fixed version. The dependency-graph
  compare ca8ef9a3...b160d82b shows the vulnerable versions removed and 0 added. The
  default-branch SBOM snapshot is stale (accelerate 1.14.0, x/net v0.47.0, torch 2.2.2, 2.9.1,
  2.11.0 and 2.13.0). No alert was dismissed. The alerts should close when the graph refreshes;
  the 2.1.0 release (plan 11-08) touches those manifests and verifies this. Open follow-up.

## Deviations

- **Task 3 has no API artifact.** No commit records the API call that enables Dependabot alerts
  and security updates. The open alerts and the 17 closed security PRs show both are enabled,
  and `.github/dependabot.yml` configures the grouped updates.
- **CodeQL fixes landed in 11-06 commits** (02e6261c, f26968d1), whose code raised the findings.
- The relock also refreshed llm-applied guide content and the relock workflow.

## Self-Check: PASSED

Every task maps to a commit. Task 3 maps only to `dependabot.yml` and the observed alert state.
The 77 open alerts are an open follow-up for plan 11-08.
