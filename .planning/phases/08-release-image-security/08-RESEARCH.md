# Phase 8: Release Image Security - Research

**Researched:** 2026-11-24
**Domain:** Container image vulnerability scanning, CVE disposition policy, release gating in GitHub Actions
**Confidence:** HIGH for repo facts and local scan data, MEDIUM for gate design and remediation estimates, LOW for base-image swap feasibility

<user_constraints>
## User Constraints

No `08-CONTEXT.md` exists. `/gsd-discuss-phase 8` has not run, so there are no locked decisions, discretion areas or deferred ideas. The constraints below come from the research request itself. They applied to this research session; the planner should keep the safety ones during execution.

- Research only. This session wrote no files except this one, built no images, made no commits and did not start, stop or remove containers or volumes. Never touch the `ds60-classroom` compose project or its volumes, the awesome-copilot MCP containers, `tender_feistel` or `condescending_kirch`.
- Scanners run only as containers against images already on the machine. Caches stay outside the repo (`~/.cache/ds60sqlpy/trivy`). Install nothing on the host.
- The user's Mac blocks public PyPI and npm. Any re-locking of Python dependencies must run in CI or behind the configured mirrors. (See Environment Availability: a host curl to pypi.org/simple returned 200 in this session, so the block may be partial or policy-level.)
- The gate must block publication on any unresolved CVE, at every severity, unless there is a documented, justified disposition with an expiry. It must record evidence of the image digest and the release candidate, and integrate with the `[publish-docker]` publish workflow.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SEC-01 | No image advances toward publication with an unresolved CVE reported by the applicable configured scan | No scanner exists today (Existing Scanning). Gate design: scan the local `tested_image_id` between `inspect` and `stage`, and re-verify at `promote` (Gate Design). Current posture and remediation levers are under Current CVE Posture and Remediation Levers. |
| RUN-01 (context) | Runtime and qualification behavior of the published images | The scan must not change qualification. It runs after `qualify`, on the same image ID. |
| REL-01 (context) | The release pipeline publishes immutable version tags plus latest aliases from qualified candidates | Scan evidence becomes a required part of the staged receipt that `promote` already validates (`scripts/docker_release.py:1118-1243`, `1302-1366`). |

Source: `.planning/REQUIREMENTS.md:36-42` (definitions), `:93-99` (phase mapping); `.planning/ROADMAP.md:135-143` (Phase 8 goal and success criteria).
</phase_requirements>

## Project Constraints (from copilot-instructions.md)

`.planning/config.json` sets `claude_md_path: ./.github/copilot-instructions.md`. Directives relevant to this phase:

- `.github/copilot-instructions.md:17`: "**Image security**: Release images must have no unresolved CVEs in the applicable scan results; rebuild or remediate affected images before publication." This is the binding constraint. The requirement says remediate or rebuild; suppression is a fallback, not the default.
- Config: `security_enforcement: true`, `security_asvs_level: 1`, `security_block_on: high`, `nyquist_validation: true`, `commit_docs: true` (the user overrode commit for this session).
- The repo uses pytest (`pyproject.toml:123-131`). `make test` runs `pytest -n 4 --dist loadgroup`. New scripts follow the existing `scripts/*.py` pattern: stdlib CLI, a `ReleaseError`-style error, exit code 2 on policy failure (`scripts/docker_release.py:1534-1665`).
- Base-image pins are partly enforced by tests: `tests/test_docker_classroom.py:514` asserts `python:3\.\d+\.\d+-slim-[a-z]+@sha256:[0-9a-f]{64}` and `:522` asserts `spark:[\w.-]+@sha256:[0-9a-f]{64}`. No test enforces digests for the other bases, which is why `gcc:14.3.0-bookworm` slipped through.

## Summary

Nothing in the DS60 repo scans images today. There is no Trivy, Grype, Scout, Snyk, OSV, Syft, cosign, `.trivyignore` or VEX in `.github/workflows`, `scripts`, `docker`, `Makefile` or `docs`. The git history (117 commits) has no CVE-driven rebuild. `.planning/codebase/CONCERNS.md:61` already notes that "No external vulnerability or software-composition audit was run". The latest publish run (44798675803, "Release DS60 1.4.3 [publish-docker]", 2026-11-20) has gate, seed, worker qualify, promote and hub-acceptance jobs but no scan job. The publish pipeline also pushes candidate tags (`ci-<rev>-<run>-<attempt>-<profile>-<arch>`) to the public `<namespace>/ds60sqlpy` Docker Hub repo at `stage`, before `promote` (`scripts/docker_release.py:1096-1104`). So the scan gate must run before `stage`, not just before `promote`.

The current CVE posture rules out a literal "zero findings" interpretation. With Trivy 0.76.2, the local `ds60sqlpy-lab:1.4.3` image shows 670 findings (13 CRITICAL, 182 HIGH). Of these, 165 have a fix available, and every fixable one is in a Python package in the venv or in the `uv` binary. None of the 505 Debian OS findings has a Debian fix. The pinned Python base (`python:3.12.16-slim-bookworm@sha256:935c3c5b...`) alone carries 392 findings, and `python:3.12-slim-bookworm` still resolves to that digest. Full SDK bases are far worse: `gcc:14.3.0-bookworm` has 13,254 findings (9,305 fixable), `spark` 6,761 (4,130 fixable), `rust` 6,149, `swift` 3,772, `golang` 3,718 and `php` 3,507. The workable meaning of "unresolved" is therefore: every fixable finding must be fixed, and every remaining finding needs a justified, expiring disposition recorded in a DS60-owned policy file. The planner should confirm this interpretation with the user (Open Question 1).

**Primary recommendation:** Add `scripts/image_scan.py`, which runs `aquasec/trivy:0.76.2@sha256:8f6bb947...` via `docker run`, scans the local tested image ID after `qualify` and before `stage` in the seed and workers jobs of both `publish-images.yml` and `targeted-images.yml`, and fails on any finding not covered by a valid entry in `security/image-cve-policy.json`. Require the resulting `scan-evidence` inside the staged receipt, and re-validate it in `promote`. Then remediate: re-lock Python dependencies, bump uv, drop or upgrade pip, digest-pin and slim the SDK bases, and add `apt-get upgrade` where Debian has fixes.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Vulnerability detection | CI runner (seed and workers jobs, per arch) | Developer Mac (optional `make scan`) | The image exists locally only on the runner that built it; scanning there avoids pushing first |
| Disposition policy (ignore or VEX entries) | Repo config (`security/`) | Human review checkpoint | Suppressions are policy decisions and must be reviewable in git with expiry |
| Gate enforcement | `scripts/docker_release.py stage` and `promote` | Workflow step order | `docker_release.py` is the only code that pushes (`docker.push` at `:1102`, `registry.put` at `:1478` and `:1506`) |
| Evidence recording | Staged receipt and `release.json` | Workflow artifact upload | Receipts already carry `tested_image_id` and are strictly schema-checked |
| Remediation | Dockerfiles, `uv.lock`, `requirements/bootstrap-uv.lock` | Base-image pins | Fixable findings are in lockfiles and bases |
| Post-publish monitoring | Scheduled workflow (optional) | None | New CVEs appear after publication; this is not a gate, but it informs rebuilds |

## Existing Scanning (Question 1)

| Search | Result | Evidence |
|--------|--------|----------|
| `trivy`, `grype`, `scout`, `snyk`, `osv`, `syft`, `sbom`, `cosign`, `vex`, `.trivyignore` across `.github/workflows`, `scripts`, `docker`, `Makefile`, `docs`, root docs | No scanner configuration | Repo-wide git grep (excluding `courses/`). The only hits were curriculum reference links and attestation-manifest handling |
| Attestation manifests | Only filtered out when resolving platform manifests, never produced or verified | `scripts/docker_release.py:296-324` |
| `git log --all --grep` for cve, trivy, vulnerab, grype, scout, security | 0 commits | 117 commits searched |
| Last publish run | No scan job | `gh run view 44798675803`: jobs gate, seed x2, 37 worker qualify, scientific-projects x2, promote, hub-acceptance x2 |
| Known concern | Recorded | `.planning/codebase/CONCERNS.md:61` |

So there are no scanned images, no severity thresholds, no failure behavior and no ignore lists or justifications. Phase 8 is greenfield for scanning.

## Image Inventory and Pins (Question 2)

### Publication path

- Trigger: push to `main` (`.github/workflows/publish-images.yml:3-5`). The `gate` job runs only if the head commit message contains `[publish-docker]` (`:18`).
- `seed` (`:49-131`), one job per arch (amd64 `ubuntu-24.04`, arm64 `ubuntu-24.04-arm`): `ci_classroom.py prepare` builds, `docker_release.py inspect` writes `work/tested-images.json` (`:85-88`), `qualify` runs, then `docker_release.py stage` pushes the candidate (`:93-104`). It uploads the receipt artifact `release-receipt-seed-<arch>-attempt-N`.
- `workers` (`:133-260`): import-seed, prepare, inspect (`:207-211`), qualify, stage (`:216-227`), receipt.
- `scientific-projects` (`:262-355`): ephemeral images, not published.
- `promote` (`:357-387`): `ci_release_status.py`, then `docker_release.py promote`, then `release.json`.
- `hub-acceptance` (`:389-430`): pulls and smoke-tests after publication.
- Targeted publishing: `.github/workflows/targeted-images.yml`, driven by `[publish-<group>]` or `[build-test-<group>]` markers (`scripts/ci_targeted_images.py:24` MARKER regex, `:54-76` `parse_marker`). It uses the same inspect, stage and promote commands (`targeted-images.yml:124`, `:141`, `:256`, `:274`, `:349`). **It is a second publication path and needs the same gate.**
- `verify-torch-package.yml`, `verify-native-package.yml` and `verify-reference-package.yml` are `workflow_dispatch` only (`verify-torch-package.yml:3-4`). They build `ds60-torch-qualification:${sha}` and so on, but never push; Docker Hub login is for pulls (`:68`). They are not publication paths. An optional non-blocking scan there gives early signal.

### Registry and tags

- Repository must equal `namespace + "/ds60sqlpy"` (`scripts/docker_release.py:109-113`); docs name `sadatnfs/ds60sqlpy` (`docs/dockerhub.md:124`).
- Candidate tag: `ci-{revision}-{run_id}-{run_attempt}-{profile}-{architecture}` (`docker_release.py:263-269`). It is pushed publicly at stage (`:1096-1104`).
- Version tag: `VERSION` for app, `VERSION-<suffix>` for workers; latest alias `latest` or `latest-<suffix>` (`:255-260`). Written as OCI indexes by `promote_release` (`:1414-1516`), version first, then latest aliases.

### Profiles published

`catalog()` (`docker_release.py:149-179`) excludes `kind == gpu` (`:171-172`). The published set is therefore the 26 non-GPU rows of `docker/classroom-images.tsv` (data rows `:2-31`, GPU rows `:19-22` are cuda-cpp, cuda-python, pytorch-cuda, tensorflow-cuda): app plus 25 workers, times amd64 and arm64, giving **52 native images per full release**.

### Base images and pin style

| Base | Pin | Used by |
|------|-----|---------|
| `python:3.12.16-slim-bookworm@sha256:935c3c5b...` | digest | `Dockerfile:1`, most workers (test-enforced at `tests/test_docker_classroom.py:514`) |
| `node:24.22.3-bookworm-slim@sha256:dc26ae92...` | digest | `Dockerfile:2`, `docker/workers/Dockerfile.node:1` (javascript, typescript) |
| `golang:1.27.4-bookworm@sha256:4fa7c968...` | digest | go worker |
| `eclipse-temurin:21-jdk-jammy@sha256:432e5472...` | digest | java worker |
| `mcr.microsoft.com/dotnet/sdk:10.0@sha256:bef136a3...` | digest | dotnet worker |
| `php:8.4.27-cli-bookworm@sha256:b3e907a1...` | digest | php worker |
| `r-base:4.6.1@sha256:ad9b3bbc...` | digest | `docker/workers/Dockerfile.r:1`; installs with `-t unstable` (`:3`) |
| `rust:1.99.1-bookworm@sha256:48b7f435...` | digest | rust worker |
| `spark:4.0.1-scala2.13-java17-python3-ubuntu@sha256:a552a335...` | digest | scala, spark-scala, spark-python (test-enforced at `tests/test_docker_classroom.py:522`) |
| `swift:6.3.3-noble@sha256:c2f3ac2e...` | digest | swift worker |
| `gcc:14.3.0-bookworm` | **tag only** | `docker/workers/Dockerfile.c:1`, `Dockerfile.cpp:1`, `compose.modules.yaml:184`, `:301` |
| `ds60sqlpy-lab:1.4.3` | local build (inherits app) | `docker/workers/Dockerfile.python-core:1` |
| `nvidia/cuda:12.8.1-devel-ubuntu24.04@sha256:520292db...` | digest | GPU only, not published |
| `postgres:17` | **tag only**, third party | `compose.yaml:6`, `compose.classroom.yaml:21`; pulled by learners, not published by DS60 |
| `kindest/node:v1.37.0@sha256:a1ed56cf...` | digest | `src/ds60sqlpy/kubernetes_module.py:43` |

## Current CVE Posture (Question 3)

Scanner: `aquasec/trivy:0.76.2@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb`, `--scanners vuln`, DB from `mirror.gcr.io/aquasec/trivy-db:2`, run 2026-11-24. Raw JSON is in `~/.cache/ds60sqlpy/scan/`. [VERIFIED: local trivy run]

### Local images (arm64, local builds, not release candidates)

| Image | Total | CRIT | HIGH | MED | LOW | UNK | Fixable |
|-------|-------|------|------|-----|-----|-----|---------|
| `ds60sqlpy-lab:1.4.3` (`sha256:42a928f2...`, Debian 12.15) | 670 | 13 | 182 | 251 | 202 | 22 | 165 (C11 H63 M66 L25) |
| `ds60sqlpy-worker-python-core:1.4.3` (`sha256:275fcdd8...`) | 670 | identical | | | | | 165 (inherits lab) |
| `python@sha256:935c3c5b` (the pinned base) | 392 | 2 | 101 | 153 | 117 | 19 | 6 (all pip 25.0.1) |
| `postgres:17` (`sha256:b60e9004...`, Debian 13.7) | 564 | 2 | 154 | | | | 191 (includes gosu Go stdlib 1.24.6, CVE-2025-68121 CRITICAL) |

Lab breakdown: 505 Debian OS findings (status affected 374, fix_deferred 117, will_not_fix 14; **0 fixable**), 123 python-pkg, 42 rustbinary (uv and uvx). Top packages by count: pillow 43, curl/libcurl4 38, libc6 30, krb5 libs 23, libsqlite3 19, virtualenv 19, filelock 12. The unfixed base criticals are CVE-2023-45853 (zlib1g) and CVE-2025-7458 (libsqlite3-0).

Fixable app findings and minimum fixed versions:

| Package | Installed | Fixed in | Where |
|---------|-----------|----------|-------|
| anyio | 4.14.1 | 4.14.2 | venv (`uv.lock`) |
| certifi | 2026.7.22 | 2026.10.18 | venv (a second copy, 2026.6.17, has no path) |
| filelock | 3.32.0 | 4.2.1 | venv |
| jupyter_server | 2.20.0 | 2.21.0 | venv |
| jupyterlab | 4.6.2 | 4.6.4 | venv |
| msgpack | 1.1.2 | 1.2.3 | no path reported |
| nbconvert | 7.17.1 | 7.17.2 | venv |
| notebook | 7.6.1 | 7.6.3 | venv |
| pillow | 12.3.0 | 13.0.0 | venv (`uv.lock:3595`) |
| pip | 25.0.1 | 26.2.0 | `/usr/local/lib/python3.12` (from base) |
| setuptools | 70.3.0 / 83.0.0 | 84.1.0 | venv |
| soupsieve | 2.9.1 | 4.0.0 | venv |
| sqlparse | 0.5.5 | 0.6.0 | venv |
| tornado | 6.5.7 | 6.6.1 | venv |
| urllib3 | 2.7.0 | 2.8.0 | venv |
| uv | 0.11.6 | 0.11.15 (PyPI advisory: 0.13.4) | system Python via `requirements/bootstrap-uv.lock:1-2` |
| virtualenv | 21.7.0 | 21.7.13 | venv (`uv.lock:6133`) |
| Rust crates in uv binary | astral-tokio-tar, quinn-proto, rand, rkyv, rustls, rustls-webpki, tar, zip 8.1.0 (CRITICAL) | fixed by a newer uv | `/usr/local/bin/uv`, `uvx` |

Note: filelock 4.x, soupsieve 4.x and pillow 13 are major bumps and need qualification. [VERIFIED: local trivy run; versions match `uv.lock`]

### Base images (remote scan, linux/amd64)

| Base | OS | Total | CRIT | HIGH | Fixable |
|------|----|-------|------|------|---------|
| node 24.22.3-bookworm-slim | Debian 12 | 269 | 1 | 43 | 19 (node-pkg) |
| php 8.4.27-cli-bookworm | Debian 12 | 3,507 | 5 | 350 | 1,270 |
| golang 1.27.4-bookworm | Debian 12 | 3,718 | 5 | 371 | 1,270 |
| rust 1.99.1-bookworm | Debian 12 | 6,149 | 36 | 886 | 2,207 |
| swift 6.3.3-noble | Ubuntu 24.04 | 3,772 | 49 | 793 | 2,873 |
| gcc 14.3.0-bookworm (tag) | Debian 12.11 | 13,254 | 226 | 2,468 | 9,305 |
| spark 4.0.1 ubuntu | Ubuntu 22.04 | 6,761 (6,562 OS, 199 jar) | 98 | 1,417 | 4,130 |
| eclipse-temurin 21-jdk-jammy | Ubuntu 22.04 | 125 | 0 | 0 | 18 |
| dotnet sdk 10.0 | Ubuntu 24.04 | 46 | 0 | 0 | 0 |
| r-base 4.6.1 | Debian forky/sid | 0 reported | | | |
| python 3.12-slim-trixie (`sha256:5e2bdb1b...`, candidate) | Debian 13.7 | 258 | 0 | 54 | 36 |
| cgr.dev/chainguard/python:latest-dev (candidate) | Wolfi | 0 | | | |

The r-base result of 0 is not evidence of a clean image. Trivy logged `WARN This OS version is not on the EOL list family="debian" version="forky/sid"` with 275 packages detected, and Debian sid has no security-tracker release mapping. Treat the R worker as **unscanned for OS packages** until it moves to a stable base or a sid-capable scanner is validated. [VERIFIED: local trivy run log]

The first JVM scans failed with `Unable to initialize the Java DB ... '--skip-java-db-update' cannot be specified on the first run`. The gate must download the Java DB as well as the main DB. [VERIFIED: ~/.cache/ds60sqlpy/scan/*.err]

The published worker images were not scanned individually in this session. Their counts will be at least those of their bases plus language packages. The pinned SDK base counts give a lower bound.

## Remediation Levers (Question 4)

No prior CVE-driven rebuild exists in git history.

1. **Re-lock Python dependencies** (`uv.lock`) to the fixed versions above. This must run in CI or a container that can reach PyPI or a mirror. It clears about 126 of the 165 fixable lab findings.
2. **Bump uv** in `requirements/bootstrap-uv.lock` (`uv==0.11.6` at `:1-2`) to at least 0.13.4 with hashes. It clears 42 rustbinary findings.
3. **Remove or upgrade base pip** in the app image (`python -m pip install --upgrade pip` from a hash lock, or delete `/usr/local/lib/python3.12/site-packages/pip*` after uv bootstrap since the venv is uv-managed). It clears 6.
4. **`apt-get upgrade`** after `apt-get update` in every Dockerfile. There is none today. This helps the SDK bases with thousands of fixable findings, and adding it costs little. It does nothing for Debian findings with no fix.
5. **Digest-pin and refresh bases.** Pin `gcc:14.3.0-bookworm` by digest, extend the pin regex test to all `FROM` lines, and refresh to the newest digests. Bump `postgres:17` to a digest pin.
6. **Slim the SDK workers.** C and C++ only need `gcc`, `g++` and `make`. They can be built `FROM` the pinned python slim base with `apt-get install gcc g++ make`, which avoids 13k findings from the full `gcc` image (which bundles a large buildpack-deps stack). The same reasoning applies to golang, rust, php and spark (multi-stage copy of the toolchain onto a slim runtime). Each needs per-worker qualification.
7. **Move to Debian 13 (trixie).** It cuts the python base from 392 to 258 findings and from 2 criticals to 0, and keeps the same Python version line. The pin test regex (`-slim-[a-z]+`) already allows `trixie`. PGDG `postgresql-client-17` must be verified for trixie.
8. **Minimal bases** (Chainguard Wolfi, Docker Hardened Images, distroless). 0 findings, but the free Chainguard tier only offers `latest`, so a Python 3.12 pin is not available [ASSUMED]. This is a larger change, deferred unless the user wants it.
9. **R worker** installs from `-t unstable` (`docker/workers/Dockerfile.r:3`). Choose between a stable-base R build (for example the rocker images on Ubuntu LTS) or a documented exception for scanner coverage.

## Gate Design (Question 5)

### Placement

The gate goes in each seed and workers job, in both workflows, **after `qualify` and before `stage`**:

```
prepare -> inspect (tested-images.json) -> qualify -> SCAN (scan-evidence.json) -> stage (requires evidence) -> receipt
promote: validate receipts + evidence freshness + policy expiry -> (optional remote rescan of candidate digests) -> write version/latest
```

Scanning before `stage` matters because `stage` pushes the public candidate tag (`docker_release.py:1096-1104`). A gate only at `promote` would still let vulnerable candidates appear on Docker Hub.

### Policy semantics (recommended, pending user decision)

- Every finding from Trivy `--scanners vuln` at all severities (`UNKNOWN` through `CRITICAL`) is **unresolved** unless one of these holds:
  - (a) it matches an entry in `security/image-cve-policy.json` with `id`, optional `profiles` and `packages` scope, `status` (`not_affected` | `no_fix_available` | `accepted_risk`), a `justification` (non-empty), `owner`, `reviewed_at`, and `expires_at` (at most 90 days after `reviewed_at`);
  - (b) for `no_fix_available` entries, the finding still has no `FixedVersion`. If a fix appears, the entry stops suppressing it.
- Any finding with `FixedVersion` cannot be accepted with `no_fix_available`, and the policy validator rejects that. `accepted_risk` on a fixable finding requires a shorter expiry (14 days recommended).
- Expired entries are errors, not warnings.
- Wildcard suppressions (for example all Debian `will_not_fix`) are not allowed. Each entry names one CVE ID. A generator script may propose entries, but a human must commit them (checkpoint).

Render the policy into a Trivy `--ignorefile` (`.trivyignore.yaml` fields `id`, `paths`, `purls`, `expired_at`, `statement`) or OpenVEX at scan time, **and** re-check the JSON output in Python. The ignorefile format is marked experimental in Trivy, so DS60 should not rely on Trivy alone for correctness. [CITED: trivy.dev filtering docs]

### Scanner invocation (per image)

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v "$TRIVY_CACHE":/root/.cache/trivy \
  aquasec/trivy:0.76.2@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb \
  image --image-src docker --scanners vuln --format json \
  --skip-db-update --skip-java-db-update --exit-code 0 \
  "$TESTED_IMAGE_ID"
```

The DB and Java DB are downloaded once per job in a separate step (`trivy image --download-db-only` and `--download-java-db-only`). DS60 code decides pass or fail, not `--exit-code`, so the evidence is always written. Mount the socket read-only and do not expose the Docker Hub token to this step.

### Evidence (`work/scan-evidence.json`)

```json
{
  "schema": 1,
  "context": {"revision": "...", "run_id": "...", "run_attempt": "...", "version": "1.4.3"},
  "architecture": "amd64",
  "scanner": {"image": "aquasec/trivy@sha256:8f6bb947...", "version": "0.76.2",
              "db_updated_at": "...", "db_next_update": "...", "java_db_updated_at": "..."},
  "policy_sha256": "...",
  "images": [{"profile": "app", "tested_image_id": "sha256:...",
              "counts": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0},
              "unresolved": [], "suppressed": [{"id": "CVE-...", "package": "...", "policy_status": "no_fix_available", "expires_at": "..."}],
              "report_sha256": "..."}]
}
```

`stage` gains `--scan work/scan-evidence.json`. It refuses unless every staged profile has an entry whose `tested_image_id` equals the inspected ID and whose `unresolved` is empty. It embeds the evidence (or its hash plus summary) in the receipt. `staged_receipt` (`:1118-1243`) checks exact key sets at `:1121-1133` and `:1146-1156`, so the schema change and tests must land together. `promotion_inputs` (`:1302-1366`) then checks that DB age at scan time was at most 24 hours, that no suppression in the evidence has expired at promote time, and that the policy hash matches the committed policy. `release.json` records the evidence per image digest. The full Trivy JSON reports are uploaded as artifacts (`scan-reports-<job>-attempt-N`, 30-day retention).

### Optional additions

- A scheduled weekly audit workflow scans the published `latest-*` tags remotely and opens an issue on new findings. It is not a gate.
- `make scan` / `python scripts/image_scan.py scan --image ds60sqlpy-lab:1.4.3` for local use, with the cache at `~/.cache/ds60sqlpy/trivy`.
- A non-blocking scan step in `verify-*-package.yml`.

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Trivy (container) | 0.76.2, `aquasec/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb` | OS and language-package CVE scan with JSON output, ignorefile and VEX | Widely used OSS scanner; already present locally; DB mirrored on `mirror.gcr.io` [VERIFIED: local docker image inspect] |
| Python stdlib (`json`, `subprocess`, `hashlib`, `datetime`) | repo Python | Policy validation, gate decision, evidence | Matches `scripts/docker_release.py` style; no new dependencies |
| pytest | repo pin | Unit tests with fixture Trivy JSON | Existing framework (`pyproject.toml:123-131`) |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| Grype (container) | v0.122.0, `anchore/grype@sha256:013e16ae96bd64108973e3e9fecec63f7ff276358d34c46c25d33e2aac96539f` | Second-opinion scan | Optional cross-check in the audit workflow; not a gate, to avoid two disagreeing policies |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Trivy via `docker run` | `aquasecurity/trivy-action` | **Rejected.** The action had 76 of 77 tags force-pushed with malicious code on 2026-03-19 [CITED: Microsoft Security Blog 2026-03-24, GHSA-69fq-xp46-6x23] |
| Trivy | Docker Scout | Requires a Docker account and entitlement; less scriptable policy |
| DS60 policy JSON | Raw `.trivyignore.yaml` only | The Trivy ignorefile is experimental, and its `statement` field is not enforced |

**Installation:** none on the host. CI runs `docker pull aquasec/trivy@sha256:8f6bb947...`.

## Package Legitimacy Audit

This phase installs no npm, PyPI or crates package. The scanner is a container image pinned by digest.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| aquasec/trivy:0.76.2 (image) | Docker Hub | image created 2026-11-05 | n/a | github.com/aquasecurity/trivy | not run through the seam (container image, not a package) | Approved with digest pin; verify the digest against the upstream release notes before first CI use |
| anchore/grype:v0.122.0 (image) | Docker Hub | n/a | n/a | github.com/anchore/grype | not run | Optional only |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none. Because of the 2026-03 Trivy release compromise (v0.69.4), the planner must add a `checkpoint:human-verify` confirming that the pinned Trivy digest matches the official release before the gate goes live.

## Architecture Patterns

### System Architecture Diagram

```
push to main (commit msg [publish-docker] | [publish-<group>] | [build-test-<group>])
        |
        v
   gate job ------------------------------------------------------------+
        |                                                               |
        v (per arch runner)                                             |
   build (ci_classroom prepare) -> inspect -> tested-images.json        |
        |                                                               |
        v                                                               |
   qualify (runtime checks)                                             |
        |                                                               |
        v                                                               |
   trivy DB + Java DB download (pinned scanner image, no secrets)       |
        |                                                               |
        v                                                               |
   image_scan.py: trivy JSON per tested_image_id                        |
        |  + security/image-cve-policy.json (validated, unexpired)      |
        v                                                               |
   unresolved == [] ? --no--> FAIL job (nothing pushed), upload report  |
        | yes                                                           |
        v                                                               |
   stage --scan evidence -> push candidate tag -> receipt(+evidence)    |
        |                                                               |
        v                                                               |
   promote: receipts + evidence + DB age + policy hash + expiry --fail--+
        | pass
        v
   write version OCI index -> latest alias -> release.json(+evidence)
        |
        v
   hub-acceptance (pull + smoke)       [optional weekly audit of latest-*]
```

### Recommended Project Structure

```
security/
  image-cve-policy.json      # dispositions, each with justification + expiry
scripts/
  image_scan.py              # download-db, scan, validate-policy, render-ignorefile
tests/
  test_image_scan.py
  fixtures/trivy/*.json      # trimmed real reports
```

### Anti-Patterns to Avoid

- **Gating only at promote:** candidates are already public on Docker Hub by then.
- **`--ignore-unfixed` as the policy:** it silently hides all Debian `affected` and `fix_deferred` findings with no record. That conflicts with "documented, justified".
- **Severity threshold (HIGH,CRITICAL only):** SEC-01 says any unresolved CVE. The config value `security_block_on: high` concerns plan-level threat findings and does not lower SEC-01.
- **Scanning by tag after push:** the scan should bind to `tested_image_id`, the same identity the receipt already carries.
- **Floating scanner tag or the GitHub action:** pin the image by digest.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vulnerability matching | Parsing dpkg/pip metadata and querying OSV | Trivy JSON | Distro-aware status (will_not_fix, fix_deferred), many ecosystems, Rust binary audit |
| Suppression format at scan time | Custom regex filters | Trivy `--ignorefile` YAML or OpenVEX rendered from the policy | Standard, with `--show-suppressed` for audit |
| Registry manifest handling | New code | Existing `docker_release.py` registry client | Already handles OCI indexes and attestation manifests |

The custom part is limited to policy validation, the pass/fail decision and evidence binding. Those are DS60-specific and short.

## Common Pitfalls

### Pitfall 1: Compromised scanner supply chain
**What goes wrong:** `trivy-action` / `setup-trivy` tags were force-pushed, and Trivy v0.69.4 was malicious (2026-03-19).
**How to avoid:** use `docker run` with a digest-pinned image, give the step no registry secrets, and mount the socket read-only.
**Warning signs:** an unpinned `uses: aquasecurity/*` in a workflow. Add a contract test in `tests/test_ci_contract.py` that forbids it.

### Pitfall 2: Unfixable Debian/Ubuntu findings make the gate permanently red
**What goes wrong:** the lab image has 505 OS findings with no Debian fix, so a strict gate blocks every release.
**How to avoid:** use the disposition policy with expiry; move to trixie or slimmer bases to shrink the list; generate entries automatically but have a human approve them.

### Pitfall 3: Candidate tags are public before promotion
See Gate Design. The scan must precede `stage`.

### Pitfall 4: Stale or missing vulnerability DB
**What goes wrong:** the scan passes against an old DB, or fails on the first run because the Java DB is missing (observed).
**How to avoid:** download both DBs per job and record `UpdatedAt`; promote rejects evidence older than 24 hours. Cache the DB via `actions/cache` keyed by date, if desired.

### Pitfall 5: Inheritance hides scope
`worker-python-core` is `FROM ds60sqlpy-lab:1.4.3` (`docker/workers/Dockerfile.python-core:1`), so app fixes must land before worker scans pass. Scan every published profile, not only bases.

### Pitfall 6: Tag-only pins
`gcc:14.3.0-bookworm` and `postgres:17` drift silently, so evidence is not reproducible. Extend the digest test beyond python and spark.

### Pitfall 7: Unsupported OS gives false clean results
r-base on sid reports 0 findings. The gate must fail (or require an explicit coverage exception) when Trivy reports an unsupported or EOL-unknown OS or zero detected packages.

### Pitfall 8: Re-locking blocked on the Mac
PyPI and npm are blocked for the user. Do the `uv lock --upgrade-package ...` remediation in CI or through the configured mirror, and verify hashes.

### Pitfall 9: Major-version fixes break the curriculum
pillow 13, filelock 4 and soupsieve 4 are major bumps. Run full qualification and notebook tests after the re-lock.

### Pitfall 10: Strict receipt schemas
`staged_receipt` and `load_tested` reject unknown keys. Update the code, the tests and the targeted workflow in the same plan, or promote will fail on old receipts. A schema version bump makes in-flight runs fail cleanly.

## Code Examples

### Policy check (sketch)

```python
# scripts/image_scan.py (sketch, DS60 style)
def unresolved(report: dict, policy: list[dict], profile: str, today: date) -> list[dict]:
    live = [e for e in policy if date.fromisoformat(e["expires_at"]) >= today
            and (not e.get("profiles") or profile in e["profiles"])]
    out = []
    for result in report.get("Results", []):
        for v in result.get("Vulnerabilities") or []:
            match = next((e for e in live if e["id"] == v["VulnerabilityID"]
                          and (not e.get("packages") or v["PkgName"] in e["packages"])), None)
            if match is None or (match["status"] == "no_fix_available" and v.get("FixedVersion")):
                out.append({"id": v["VulnerabilityID"], "package": v["PkgName"],
                            "installed": v["InstalledVersion"], "fixed": v.get("FixedVersion", ""),
                            "severity": v["Severity"], "target": result["Target"]})
    return out
```

### Workflow step (seed job, between qualify and stage)

```yaml
- name: Scan qualified images for CVEs
  run: |
    python scripts/image_scan.py download-db --cache "$RUNNER_TEMP/trivy"
    python scripts/image_scan.py scan --tested work/tested-images.json \
      --policy security/image-cve-policy.json --cache "$RUNNER_TEMP/trivy" \
      --output work/scan-evidence.json --reports work/scan-reports
- uses: actions/upload-artifact@<pinned-sha>
  if: always()
  with: {name: scan-reports-seed-${{ matrix.arch }}-attempt-${{ github.run_attempt }}, path: work/scan-reports, retention-days: 30}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `aquasecurity/trivy-action@<tag>` | Digest-pinned scanner image or verified binary | 2026-03 compromise | Do not use tag-pinned actions for scanners |
| `.trivyignore` plain list | `.trivyignore.yaml` with `expired_at`, or OpenVEX | Trivy 0.4x+ | Expiring suppressions are supported natively (experimental) |
| Full SDK base images | Slim or hardened bases (Wolfi, DHI, distroless) | ongoing | Order-of-magnitude fewer findings |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | "Unresolved" means fixable findings are fixed and unfixable ones carry justified, expiring dispositions | Gate Design | If the user wants literal zero, almost every base must change to Wolfi/DHI, which turns Phase 8 into a platform migration |
| A2 | The free Chainguard tier cannot pin Python 3.12 | Remediation | A cheaper zero-CVE path may exist |
| A3 | Building C/C++ workers on python-slim plus apt gcc keeps behavior equal to the `gcc:14.3.0` image | Remediation | Compiler version changes (Debian gcc 12 vs 14) could break C/C++ lessons; pinning gcc 14 may need trixie (gcc 14) |
| A4 | PGDG publishes `postgresql-client-17` for trixie | Remediation | The trixie move for the app would be blocked |
| A5 | A 24-hour DB freshness bound and a 90-day maximum expiry are suitable | Gate Design | Too strict causes flaky promotes; too loose weakens the gate |
| A6 | Published worker images have at least their base counts | Posture | Only the lab and python-core images were scanned in full |
| A7 | The OpenVEX handling detail (status and justification only, newest timestamp wins) | Gate Design | Comes from a third-party article; mitigated by DS60 re-checking the JSON itself |

## Open Questions

1. **Meaning of "unresolved"** (blocking). What we know: there are 505 unfixable OS findings in the app alone. Recommendation: adopt A1, with a human checkpoint approving the initial disposition file.
2. **Is `postgres:17` in scope?** It is third party, pulled by learners and referenced in release compose files. Recommendation: digest-pin it and scan it as a "release-referenced" image with the same policy, but do not block the DS60 publish on upstream findings that have no fix; record them instead.
3. **Base strategy.** Choose between trixie, slim rebuilds of SDK workers, and Wolfi/DHI. Recommendation: trixie for the python family, slim rebuilds for gcc, rust, golang and php, and a reviewed exception or stable-base move for R.
4. **R worker coverage.** Trivy cannot assess sid. Recommendation: move to a stable base, or record an explicit coverage exception that expires and is reviewed per release.
5. **Promote-time remote rescan.** It costs time across 52 images. Recommendation: rely on evidence freshness at first; add a remote rescan only if DB age between stage and promote exceeds the bound.
6. **arm64 scanning.** It runs on the native arm64 runner per job; the Trivy image is multi-arch. Arm-specific findings can differ, so each architecture needs its own evidence.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker (Mac) | Local scans | yes | server 29.9.3, linux/arm64 | none |
| Trivy image | Gate | yes, local | 0.76.2 `@sha256:8f6bb947...` | pull by digest in CI |
| Grype image | Optional cross-check | yes, local | v0.122.0 `@sha256:013e16ae...` | skip |
| Trivy DB (`mirror.gcr.io/aquasec/trivy-db:2`) | Gate | yes (downloaded, 136MB) | n/a | ghcr.io/aquasecurity/trivy-db |
| Trivy Java DB | JVM images | yes (downloaded this session) | n/a | none; required for java, scala, spark |
| ghcr.io, registry-1.docker.io, mirror.gcr.io | Pulls | reachable (HTTP 401 auth challenge) | n/a | n/a |
| Grype DB endpoint | Optional | reachable (HTTP 200) | n/a | n/a |
| pypi.org/simple from host | Re-lock | curl returned 200 this session; the user reports it is blocked | n/a | CI re-lock |
| gh CLI with `sadatnfs` token | CI log inspection | yes | n/a | n/a |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** PyPI access for re-locking (do it in CI).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (`pyproject.toml:123-131`) |
| Config file | `pyproject.toml` |
| Quick run command | `python -m pytest tests/test_image_scan.py tests/test_docker_release.py tests/test_ci_contract.py -x` |
| Full suite command | `make test` (`pytest -n 4 --dist loadgroup`) |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SEC-01 | Unsuppressed finding (any severity) yields non-empty `unresolved` and exit 2 | unit | `pytest tests/test_image_scan.py -k unresolved -x` | no, Wave 0 |
| SEC-01 | Expired, malformed, wildcard or justification-less policy entry is rejected | unit | `pytest tests/test_image_scan.py -k policy -x` | no, Wave 0 |
| SEC-01 | `no_fix_available` entry stops suppressing once `FixedVersion` appears | unit | `pytest tests/test_image_scan.py -k fixed_version -x` | no, Wave 0 |
| SEC-01 | Unsupported OS or zero-package report fails closed | unit | `pytest tests/test_image_scan.py -k coverage -x` | no, Wave 0 |
| SEC-01 | `stage` refuses with missing, mismatched-ID or dirty evidence | unit | `pytest tests/test_docker_release.py -k scan -x` | file exists (34 tests); new cases |
| SEC-01 | `promote` rejects stale DB, expired suppression, policy hash mismatch | unit | `pytest tests/test_docker_release.py -k promote_scan -x` | new cases |
| SEC-01 | Both publish workflows run the scan between qualify and stage, scanner pinned by digest, no `aquasecurity/` actions | contract | `pytest tests/test_ci_contract.py -x` | file exists (14 tests); new cases |
| SEC-01 | Every `FROM` / compose `image:` is digest-pinned | contract | `pytest tests/test_docker_classroom.py -k pin -x` | extend `:514-522` |
| SEC-01 | Real gate on real images | CI integration | `[build-test-<group>]` targeted run, then the evidence artifact | manual review |

### Sampling Rate

- **Per task commit:** the quick run command.
- **Per wave merge:** `make test`.
- **Phase gate:** full suite green, plus one `[build-test-*]` run whose evidence shows empty `unresolved` for every image, before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `tests/test_image_scan.py`
- [ ] `tests/fixtures/trivy/` (trimmed reports: clean, fixable, unfixed-only, sid/unsupported, rustbinary)
- [ ] `security/image-cve-policy.json` schema plus an empty starter file

## Security Domain

### Applicable ASVS Categories (Level 1)

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | n/a |
| V3 Session Management | no | n/a |
| V4 Access Control | partial | Scan step gets no registry secrets; socket mounted read-only |
| V5 Input Validation | yes | Strict schema validation of the policy file and the Trivy JSON (exact keys, ISO dates, ID regex) |
| V6 Cryptography | no | Hash evidence with `hashlib.sha256` only |
| V10 Malicious Code / Supply chain | yes | Digest-pinned scanner and bases; no third-party scanner actions |
| V14 Configuration / Dependencies | yes | Known-vulnerable component gate (the SEC-01 core) |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious scanner release or action tag rewrite | Tampering, Elevation | Digest pin, no secrets in step, contract test |
| Blanket suppression hides real risk | Repudiation | Per-CVE entries, justification, owner, expiry, human checkpoint |
| Scan of a different image than the one published | Spoofing | Bind evidence to `tested_image_id`, which `stage` and `promote` re-check |
| Vulnerable candidate exposed publicly | Information disclosure | Gate before `stage` |
| Stale DB gives a false pass | Tampering | Record DB `UpdatedAt`; promote bound |

## Recommended Plan Breakdown (Question 6)

| Plan | Wave | Scope | Depends |
|------|------|-------|---------|
| 08-01 Scan gate tooling and policy | 1 | `scripts/image_scan.py` (download-db, scan, validate-policy, render-ignorefile), `security/image-cve-policy.json` schema, fixtures, `tests/test_image_scan.py`; `docker_release.py stage --scan` and promote checks with receipt schema changes; digest-pin contract test for all bases | none |
| 08-02 Remediation | 2 | Re-lock `uv.lock` (in CI), bump uv to at least 0.13.4 in `bootstrap-uv.lock`, remove or upgrade base pip, `apt-get upgrade` in all Dockerfiles, digest-pin gcc and postgres, slim C/C++ (and others if qualified), trixie evaluation, R coverage decision; generate the remaining disposition entries for **human review checkpoint** | 08-01 (needs the scanner to measure) |
| 08-03 Workflow integration and proof | 2 or 3 | Scan steps in `publish-images.yml` seed/workers and `targeted-images.yml`, artifact upload, evidence in `release.json`, optional weekly audit; `[build-test-<group>]` dry run with evidence review; `checkpoint:human-verify` on the Trivy digest | 08-01; proof run needs 08-02 |

08-02 and the workflow wiring in 08-03 can proceed in parallel once 08-01 lands. The final proof run waits for both.

## Sources

### Primary (HIGH confidence)
- Repo files read this session: `.github/workflows/publish-images.yml`, `targeted-images.yml`, `verify-torch-package.yml`; `scripts/docker_release.py`; `scripts/ci_targeted_images.py`; `docker/classroom-images.tsv`; `Dockerfile`; `docker/workers/Dockerfile.*`; `compose*.yaml`; `requirements/bootstrap-uv.lock`; `uv.lock`; `tests/test_docker_classroom.py:500-522`; `.planning/*`; `.github/copilot-instructions.md:17`.
- Local Trivy 0.76.2 scans, JSON in `~/.cache/ds60sqlpy/scan/`.
- `gh run view 44798675803` (sadatnfs/ds60sqlpy).

### Secondary (MEDIUM confidence)
- trivy.dev docs: filtering (`--ignorefile`, `.trivyignore.yaml`, `--ignore-unfixed`, `--ignore-status`) and VEX (trivy.dev/docs/v0.53/guide/supply-chain/vex).
- Microsoft Security Blog 2026-03-24; NHS cyber alert; GHSA-69fq-xp46-6x23 (Trivy and trivy-action compromise).

### Tertiary (LOW confidence)
- A third-party article on Trivy OpenVEX statement selection (firewallsync).
- Chainguard free-tier tag availability (training knowledge).

## Metadata

**Confidence breakdown:**
- Existing state and inventory: HIGH. Read from the files and the CI run.
- CVE posture: HIGH for scanned images at the 2026-11-24 DB; the numbers will drift daily.
- Gate design: MEDIUM. It fits the existing receipt flow, but the policy semantics need user sign-off.
- Remediation impact: MEDIUM. Base swaps need qualification.

**Research date:** 2026-11-24
**Valid until:** 2026-12-08 (CVE data is fast-moving; re-scan before planning if older)

## Five-Line Summary

1. No CVE scanning exists anywhere in DS60; candidates are pushed publicly at `stage` before `promote`, so the gate must sit between `qualify` and `stage` in both publish workflows.
2. Lab 1.4.3 has 670 findings (13 critical); all 165 fixable ones are Python packages or the uv binary, and none of the 505 Debian OS findings has a fix.
3. SDK bases are the bulk of the risk (gcc 13,254, spark 6,761, rust 6,149), `gcc` and `postgres` are tag-only, and r-base on sid is effectively unscanned.
4. Use digest-pinned Trivy 0.76.2 via `docker run` (never trivy-action, compromised in 2026-03), a DS60 policy file with justified, expiring per-CVE dispositions, and evidence bound to `tested_image_id` in receipts.
5. Three plans: gate tooling, remediation (re-lock, uv bump, pip, apt upgrade, slim bases), workflow integration plus a `[build-test-*]` proof run, with a user decision on what "unresolved" means.
