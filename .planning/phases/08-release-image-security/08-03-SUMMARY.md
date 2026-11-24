---
phase: 08-release-image-security
plan: 03
subsystem: release-image-security
status: partial
requirements: [SEC-01]
tags: [trivy, cve, trixie, locks, postgres, policy]
requires: [08-01]
provides:
  - python family on python:3.12.16-slim-trixie and node:24.22.3-trixie-slim digests
  - hash-locked pip 26.3 and uv 0.13.8 bootstrap locks
  - postgres:17.12-trixie digest pin in compose, launcher and mirror list
  - docker/cve-policy.json with 60 pending-owner entries for unfixed Debian 13 HIGH findings
  - .github/workflows/relock-python.yml (not pushed, not dispatched)
affects: [08-02, 08-04]
tech-stack:
  added: []
  patterns: [apt-get upgrade in every python-family image, base pip removed after use, Temurin JDK copied from the pinned spark image]
key-files:
  created:
    - requirements/bootstrap-pip.lock
    - .github/workflows/relock-python.yml
    - work/08-03/postgres/Dockerfile (scratch prototype)
  modified:
    - Dockerfile
    - docker/workers/Dockerfile.{bayesian,data,data-platforms,java,jax,julia,node,python-web,spark,stan,tensorflow,torch}
    - docker/kubernetes/Dockerfile.{fixture,worker}
    - packages/spark-likelihood/Dockerfile
    - packages/spark-tmbad/Dockerfile
    - docker/workers/requirements-{torch,python-web,data-engineering}.{amd64,arm64}.lock
    - requirements/bootstrap-uv.lock
    - compose.yaml
    - compose.classroom.yaml
    - scripts/classroom.sh
    - docker/registry-mirrors.env.txt
    - docker/cve-policy.json
    - tests/test_docker_classroom.py
    - tests/test_classroom_launchers.py
    - tests/test_image_scan.py
decisions:
  - Remove the base interpreter pip from every image after it is used (or immediately where nothing installs Python packages) instead of upgrading it and keeping it.
  - Replace Debian openjdk-17 (absent from Debian 13) with the Temurin 17 runtime copied from the already pinned spark image.
  - Drop libexpat1 from the app image; nothing in the trixie image links libexpat.so.1 (CPython uses its bundled expat).
  - Accept unfixed Debian 13 HIGH findings only as 30-day pending-owner entries with package-specific justifications; no misconfig entries.
  - Do not adopt the postgres derivative image without an owner decision; record it as a Known blocker for 08-04.
metrics:
  completed: 2026-11-23
actuals:
  tasks: 3
  commits: 0
plan_head_before: 5ad22de5443ca3567e221032de0580ee224f4621
plan_head_after: 5ad22de5443ca3567e221032de0580ee224f4621
---

# Phase 8 Plan 03: Python family and postgres image remediation Summary

The python family moved to Debian 13 (trixie) digests with apt security upgrades, hash-locked pip/uv bootstraps, base pip removed and patched worker locks. Critical findings dropped from 13 to 0 in the app image and from 8 to 0 in python-core. python-web and data-engineering now scan with no blocking findings. Postgres is digest-pinned on 17.12-trixie, and a prototype derivative proves the remaining postgres fixable findings can be cleared.

No commits were made (orchestrator rule); all changes are in the working tree.

## Scan results (Trivy DB 2026-11-24, same DB before and after)

| Image | Before (1.4.3) C/H/M/L/U | Before blocking | After C/H/M/L/U | After blocking |
|---|---|---|---|---|
| app (lab) | 13/184/252/202/22 | 321 (168 fixable, 32 misconfig, 121 unaccepted) | 0/61/119/165/19 | 35 (3 fixable, 32 misconfig), 60 accepted |
| python-core | 8/119/164/174/22 | 182 (118 fixable, 64 unaccepted) | 0/61/119/165/19 | 3 (3 fixable), 60 accepted |
| python-web | not scanned at 1.4.3 (image absent locally) | n/a | 0/53/74/79/16 | 0, 53 accepted |
| data-engineering | not scanned at 1.4.3 | n/a | 0/53/80/80/16 | 0, 53 accepted |
| scala-jvm | not scanned at 1.4.3 | n/a | 8/140/171/86/16 | 246 (189 fixable Spark jars, 57 unaccepted) |
| postgres upstream 17.12-trixie@223efeb | n/a | n/a | 2/154/210/172/26 | 83 fixable (krb5 x56, Go stdlib in gosu x26, zlib1g x1) |
| postgres derivative prototype | n/a | n/a | 1/72/110/165/26 | 0 |

Evidence: `work/p8-scan/lab-1.4.3-db20261124.json`, `python-core-1.4.3-db20261124.json` (before, reports in `reports-before-08-03/`), `lab-trixie.json` (= `lab-remediated.json`), `python-core-trixie.json`, `python-web-trixie.json`, `data-engineering-trixie.json`, `scala-jvm-trixie.json`, `postgres-pinned.json`, `postgres-derivative.json` (reports in `reports-08-03/`).

Measurement caveat: the app and python-core images were built from a clean `git archive HEAD` context plus my changed files and a scratch, proxy-resolved `uv.lock` (prefect 3.9.3, packaging 26.3, virtualenv 21.15.7). That lock records Azure feed URLs, so it is measurement only. The committed `uv.lock` is unchanged until the relock workflow runs.

## What changed

- **Bases:**
  - Every `python:3.12.16-slim-bookworm` ref became `python:3.12.16-slim-trixie@sha256:5e2bdb1b...`.
  - The node refs became `node:24.22.3-trixie-slim@sha256:af02d57b...`.
  - PGDG publishes `postgresql-client-17` for trixie-pgdg on amd64 and arm64 (3 entries each, checked against the Packages indexes).
- **Every python-family image:** `apt-get upgrade -y` on its first apt layer.
- **Bootstrap locks:** `requirements/bootstrap-pip.lock` (pip 26.3) and `requirements/bootstrap-uv.lock` (uv 0.13.8, the newest on the reachable proxy), both full-hash and public-source only.
- **pip removal:**
  - Images that install Python packages upgrade pip from the bootstrap lock for the locked install, then uninstall it.
  - Images that install no Python packages (julia, java, node, spark, kubernetes fixture) uninstall the base pip directly.
  - The app removes base pip once uv is in place.
  - The learner venv's pip stays (pyproject `pip>=24.0`).
- **Java:** Debian 13 has no `openjdk-17-jdk-headless`. Dockerfile.spark and both spark packages now copy `/opt/java/openjdk` (Temurin 17.0.18) from the pinned spark image. `java -version` was verified in scala-jvm.
- **app:** `libexpat1` removed. Zero consumers of `libexpat.so.1` were found (control: 5 consumers of libncursesw found by the same search), and `pyexpat`/xml/sqlite3/ssl/psql all work in the rebuilt image.
- **Worker locks:**
  - torch: setuptools 78.1.0 to 84.2.1.
  - python-web: dnspython 2.9.0 to 2.9.2.
  - python-web and data-engineering: opentelemetry api/sdk/proto 1.45.1 to 1.45.2 and semantic-conventions 0.66b1 to 0.66b2, moved together because sdk pins api exactly.
  - Hashes were checked against pypi.org JSON.
  - The rebuilt images import fastapi, dns, mlflow, dbt and opentelemetry.sdk.
- **Postgres:** `postgres:17.12-trixie@sha256:223efeb196329b55b3b9a13db144956411dbc18e727e59f681c3e0aede6475cf` in compose.yaml, compose.classroom.yaml, scripts/classroom.sh (2 places) and registry-mirrors.env.txt (mirror prefix). 17, 17-trixie, 17.12 and 17.12-trixie all resolve to this digest, so there is no newer 17.x.
- **Policy:**
  - 60 `pending-owner` entries, expiring after 30 days.
  - Scope: unfixed Debian 13 HIGH findings across app, python-core, python-web and data-engineering. Packages: util-linux family, curl/libcurl4t64, perl family, ncurses, sqlite, openssl, libsystemd0/libudev1, libacl1.
  - Each justification states the verified reason the package cannot be removed.
  - No misconfig entries; no fixable findings accepted.
- **Tests:**
  - test_docker_classroom asserts one trixie python ref, one trixie node ref and one pinned postgres ref.
  - test_classroom_launchers uses the pinned mirror postgres ref.
  - test_image_scan's starter-file test now checks structure, not emptiness.

## Known blockers and owner decisions

1. **uv.lock relock (pending orchestrator action).** files.pythonhosted.org is blocked here, so `uv.lock` was not regenerated. The orchestrator should push `.github/workflows/relock-python.yml` to main, then:
   `export GH_TOKEN=$(env -u GH_TOKEN gh auth token --user sadatnfs)`
   `gh workflow run relock-python.yml --repo sadatnfs/ds60sqlpy --ref main -f packages="anyio certifi filelock jupyter-server jupyterlab msgpack nbconvert notebook packaging pillow pip prefect setuptools soupsieve sqlparse tornado urllib3 virtualenv"`
   then `gh run download <run-id> -n relocked-uv-lock`, copy uv.lock in, rebuild the app and rescan. Until then the committed lock still carries the 1.4.3 fixable Python findings (anyio, certifi, filelock, jupyter, pillow, etc.).
2. **setuptools 70.3.0 in pip's vendored SBOM (3 fixable in app and python-core).**
   - Source: `pip/_vendor/bom.cdx.json` of pip 26.3 in /opt/course/.venv.
   - pip vendors only pkg_resources from setuptools 70.3.0; the CVEs affect package_index/sdist code that pip does not ship. No pip release changes this.
   - Options: drop pip from the learner venv (learners use `uv pip`), add VEX/not-affected support to image_scan.py, or wait for upstream. Deleting the SBOM file to pass the scanner was rejected as evidence tampering.
3. **Misconfig (32 in app).** 31 DS-0002 and 1 KSV-0056 come from course Dockerfiles and manifests shipped under /opt/course by design. Fixing them means changing course content or excluding them from the image (Rule 4).
4. **Postgres.**
   - Upstream 17.12-trixie keeps 83 fixable findings: krb5 deb13u1 (fixed deb13u2), zlib1g, and gosu 1.20 built with go1.24.6.
   - Prototype `work/08-03/postgres/Dockerfile` applies `apt-get upgrade` and rebuilds gosu 1.20 from the sha256-pinned tag tarball with golang 1.26 (go1.26.11). It scans with blocking 0 and starts (initdb and server reached "ready to accept connections" through gosu).
   - Adopting it means publishing a new DS60 image: owner decision for 08-04.
5. **scala-jvm.** 189 fixable findings come from Spark 4.0.1's own jars (jackson, netty, log4j, jetty, guava, etc.). `spark:4.3.0-scala2.13-java17-python3-ubuntu` exists (index `sha256:6f4beaaa...`) but could not be pulled (mirror.gcr.io quota) and is a course-runtime upgrade: owner decision.
6. **Remaining unfixed Debian HIGHs** are accepted for 30 days only and must be re-checked when trixie-security ships fixes.
7. **curl** stays in the app because course guides (apache-data-platforms) use it in the learner terminal. Purging it after the PGDG key fetch is an owner option.

## Deviations from Plan

- [Rule 3] `uv.lock` not relocked locally; authored `.github/workflows/relock-python.yml` (extra file: workflow_dispatch only, contents: read, actions pinned by SHA, uploads uv.lock artifact, `runs-on: ubuntu-latest` to satisfy test_ci_contract).
- [Rule 3] uv 0.13.8 instead of 0.13.9 (not on the reachable proxy).
- [Rule 3] Ref swap only, outside files_modified: `.env.example`, `compose.modules.yaml`, `compose.classroom.kubernetes.yaml`, `docker/formatting/Dockerfile` (needed for the single-ref test and the bookworm grep).
- [Rule 1] `packages/spark-likelihood/docs/PREPARATION.md` default base text updated to trixie (plan verify grep covers packages/).
- [Rule 3] `tests/test_image_scan.py` starter test asserted an empty policy, contradicting Task 3.
- [Rule 1] Removed openjdk-17 (absent from Debian 13) in favour of the copied Temurin JDK; `libssl3` became `libssl3t64` in spark-tmbad.
- [Rule 2] Removed unused `libexpat1` from the app; removed base pip from images.
- Builds used `mirror.gcr.io/library/...` base args (same digests) because Docker Hub auth returned 429, from a clean `git archive` context because other agents' uncommitted courses/ edits make `compile_lesson_tex --check-inputs` fail in the working tree.
- Postgres before/after used the upstream image pulled by digest; the derivative stays a scratch prototype.

## Verification (real results)

- T1 `lab-remediated.json` no-fixable check: FAILED, 3 setuptools (pip SBOM) findings, see blocker 2.
- T1 `grep packagefeedproxy uv.lock requirements/bootstrap-*.lock`: no matches (rc 1), passes.
- T2 `git grep slim-bookworm -- Dockerfile docker packages compose*.yaml`: no matches after the PREPARATION.md fix, passes.
- T2 `python-core-trixie.json` no-fixable check: FAILED, same 3 setuptools findings.
- T3 `validate-policy`: `policy valid: 60 entries (60 pending-owner)`.
- T3 `git grep 'postgres:17([^.]|$)'` in compose/launcher/mirror files: no matches, passes.
- `pytest -n 0 tests/test_docker_classroom.py tests/test_classroom_launchers.py tests/test_ci_contract.py tests/test_image_scan.py`: 310 passed, 1 failed (test_policy_starter_file_is_valid) before the test fix; test_image_scan.py then 69 passed. Earlier failures in test_ci_contract (runner) and test_docker_classroom (node regex) were fixed and pass (16 passed).
- `ruff check`, `ruff format --check`, `mypy src`: all pass.
- `./scripts/lint-repo --language docker`: passed (48 files).
- `./scripts/lint-repo` (full): failed only on `scripts/check_classroom_ui.mjs:1334` javascript syntax error, a file another agent has modified (uncommitted, +439 lines); not touched by 08-03.
- `docker compose -f compose.yaml -f compose.modules.yaml --profile '*' config -q`: ok.
- Dash check over every file I changed: none found.
- actionlint: not installed, not run.

## Known Stubs

None.

## Self-Check: PASSED

Created files exist (bootstrap-pip.lock, relock-python.yml, work/08-03/postgres/Dockerfile, scan evidence). No commits to check (commits: 0 by orchestrator rule). Disposable images `ds60-p8-scan/*` (10) removed; work/test-tmp-08-03 and work/08-03/ctx deleted.

## Reconciliation (finished under 08-04, 2026-11-24)

After this partial report, the stopped 08-03 executor left uncommitted owner-item work.
Plan 08-04 reviewed, finished and verified it. The details are in `08-04-SUMMARY.md` and
`08-SCAN-LEDGER.md`.

- **Postgres:** `docker/postgres/Dockerfile` (gosu 1.20 built with Go 1.26.11) is wired
  into `scripts/classroom.sh`.
  - It is built before the services and tagged `ds60sqlpy-postgres:<release version>`.
  - It is pulled only when `DS60_POSTGRES_IMAGE` is overridden.
  - Launcher tests were updated.
  - Scanned as a reference: 0 fixable, 73 unfixed findings reported. The smoke test passed.
  - Hub publishing remains a follow-up.
- **pip prune:** verified inside the built app image (pip commands and a scratch install).
  python-core inherits it. The app, python-core, python-web and data-engineering rescans
  pass with 0 fixable findings.
- **Misconfigurations:** the learner Dockerfiles end non-root. The DS-0002 entries are
  kept as reviewed D-06 misconfig entries, plus one for the course postgres example.
  `test_policy_starter_file_is_valid` now accepts misconfig entries.
- **spark-deploy-016 access.yaml change:** was already committed (b1847ca7). The course
  and parity tests pass.
- **Validation:** actionlint, `lint-repo --language docker` and the dash scan were run
  under 08-04, and all are clean.
- **Status:** the owner items are closed except Spark, which is still blocked by fixable
  shaded-jar findings (Rule 4, see 08-04).
