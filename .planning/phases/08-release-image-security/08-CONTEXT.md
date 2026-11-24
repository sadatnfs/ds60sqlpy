# Phase 8 context: release image security

**Requirement:** SEC-01. Every image intended for publication is scanned with the
current configured vulnerability checks and has no unresolved detected CVEs;
affected images are remediated and rescanned before publication.

**Source:** owner decisions supplied with the planning request on 2026-11-23,
recorded here in place of a `/gsd-discuss-phase 8` session. The owner requires
every container image built for his tools to be fully CVE-free so internal
compliance scanners do not flag them, rebuilding components from source when
needed. Primary research: `08-RESEARCH.md` (Trivy 0.76.2 scans of 2026-11-24).

## Starting point (from research)

- Nothing scans images today (`.planning/codebase/CONCERNS.md:61`). `stage`
  pushes public candidate tags before `promote`
  (`scripts/docker_release.py:1096-1104`), so a promote-only gate is too late.
- `ds60sqlpy-lab:1.4.3` has 670 findings (13 CRITICAL, 182 HIGH); all 165
  fixable ones are Python packages in the venv, base pip 25.0.1 or the uv
  0.11.6 binary. None of the 505 Debian 12 OS findings has a Debian fix.
- SDK bases dominate: gcc 13,254 findings (9,305 fixable), spark 6,761, rust
  6,149, swift 3,772, golang 3,718, php 3,507. `gcc:14.3.0-bookworm` and
  `postgres:17` are tag-only pins. `r-base` on sid reports 0 findings because
  Trivy cannot map sid; it is unscanned, not clean.
- `python:3.12-slim-trixie` drops the python base from 392 findings (2
  CRITICAL) to 258 (0 CRITICAL).

## Decisions

- **D-01 Scanner.** Trivy 0.76.2 pinned by digest
  (`aquasec/trivy:0.76.2@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb`),
  always run via `docker run`. Never use `aquasecurity/trivy-action` or
  `aquasecurity/setup-trivy` (compromised 2026-03-19). Caches live outside the
  repo: `~/.cache/ds60sqlpy/trivy` locally, `actions/cache` (pinned by SHA) in
  CI. Both the vulnerability DB and the Java DB are downloaded. The scan step
  receives no registry secrets and mounts the Docker socket read-only.
- **D-02 Gate position.** The scan runs between `qualify` and `stage` in the
  seed and workers jobs of BOTH `.github/workflows/publish-images.yml` and
  `.github/workflows/targeted-images.yml`, in build-test mode as well as publish
  mode, so nothing vulnerable is ever pushed publicly. `stage` refuses without
  matching evidence. `promote` re-verifies the scan evidence bound to each
  `tested_image_id` and fails if the vulnerability DB used for any evidence is
  older than 24 hours at promote time.
- **D-03 Fixable findings always block.** Every finding with an available fix
  (non-empty `FixedVersion`), at any severity including UNKNOWN, is unresolved
  and must be fixed by upgrading or rebuilding. The policy file cannot accept a
  fixable finding; an entry that matches a finding which has since gained a fix
  stops suppressing it.
- **D-04 Unfixed findings.** Findings without a fix are driven toward zero by
  base-image strategy. An unfixed CRITICAL or HIGH finding blocks unless a live
  policy entry covers it. Unfixed MEDIUM and LOW findings are reported and
  recorded in the evidence ledger without blocking.
- **D-05 DS60 policy file.** Accepted entries live in a DS60-owned JSON file
  (not a raw `.trivyignore`). Each entry names one finding id, the package,
  the image profile(s), a justification, a reviewer field and an expiry at
  most 90 days after review. No wildcards. The gate fails on any expired entry
  and on malformed entries; DS60 Python code decides pass or fail from the
  full Trivy JSON (Trivy runs with `--exit-code 0`, no ignorefile).
- **D-06 Secrets and misconfig.** The app image is scanned with
  `--scanners vuln,secret,misconfig`. Workers use `vuln` (plus `secret`).
- **D-07 Python family on trixie.** Move the python image family to Debian
  trixie slim (`python:3.12.x-slim-trixie@sha256:...`) where scans show fewer
  findings and qualification still passes. The single-python-reference test
  (`tests/test_docker_classroom.py:497-522`) keeps every python reference
  identical, including `packages/*/Dockerfile` and `docker/kubernetes/*`.
- **D-08 Slim SDK workers.** Rebuild C and C++ (gcc) workers on slim bases with
  only the toolchain packages they need; apply the same approach to go, rust,
  php and spark where feasible. Where a fixable finding is inside a bundled
  component, rebuild or replace that component from pinned source.
- **D-09 R off sid.** Move the R worker off Debian sid to a stable, scannable
  base (for example `rocker/r-ver:4.6.x` pinned by digest, or Debian trixie
  `r-base` packages). Only if that fails qualification, record an expiring
  coverage exception in the policy file.
- **D-10 Digest pins everywhere.** Every base image is pinned by digest,
  including `gcc` and `postgres:17`, in Dockerfiles, compose files, the
  launcher and `docker/registry-mirrors.env.txt`; a contract test enforces it.
- **D-11 postgres:17 is in scope.** Pin by digest and scan it as a
  release-referenced third-party image. Its unfixed upstream findings and its
  fixable MEDIUM/LOW findings are recorded without blocking; fixable CRITICAL or
  HIGH findings block and are resolved by moving to a newer upstream digest.
- **D-12 Python dependency remediation.** Re-lock `uv.lock` with fixed
  versions; bump `requirements/bootstrap-uv.lock` to uv >= 0.13.4 with every
  published file hash; remediate base pip; re-compile the hash-locked worker
  requirement files that carry fixable findings.
- **D-13 Package feeds.** On the owner's Mac public PyPI and npm are blocked;
  use `https://packagefeedproxy.microsoft.io/pypi/simple/` (already configured
  in `~/.config/uv/uv.toml` and pip.conf). CI uses public indexes. Committed
  lockfiles must never record the proxy URL.
- **D-14 Human review without blocking.** Policy entries carry a `reviewer`
  field. In this autonomous run the agent writes proposed entries with
  `"reviewer": "pending-owner"`; Phase 10 surfaces them to the owner. No plan
  adds a blocking human checkpoint.
- **D-15 Proof and local safety.** A `[build-test-<group>]` push (or a
  `workflow_dispatch` run) proves the gate on real images on both amd64 and
  arm64. Locally, the docker-run Trivy may scan images already built under the
  shared tags read-only. Never retag, rebuild over or push the shared `1.4.3`
  tags. Never touch the owner's `ds60-classroom` project or volumes, the
  awesome-copilot MCP containers, `tender_feistel` or `condescending_kirch`.
  Local remediation builds use the isolated repository prefix `ds60-p8-scan/`
  and are removed by exact tag after scanning.
- **D-16 GitHub access.** Pushing to `sadatnfs/ds60sqlpy` main and dispatching
  workflows is authorized. Authenticate with
  `export GH_TOKEN=$(env -u GH_TOKEN gh auth token --user sadatnfs)`.
- **D-17 Style.** No em or en dashes in any written file; American English.
- **D-18 Verification commands.**
  `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp <files>`,
  `.venv/bin/ruff check src scripts tests`,
  `.venv/bin/ruff format --check src scripts tests`, `.venv/bin/mypy src`,
  `set -a; . ./.env; set +a; ./scripts/lint-repo` (actionlint, shellcheck,
  hadolint).

## The agent's discretion (choices made by the planner)

- Policy path and schema: `docker/cve-policy.json`, schema 1, exact key set
  `id`, `kind` (`vulnerability` | `misconfig` | `coverage`), `package`,
  `images`, `justification`, `reviewer`, `reviewed_at`, `expires_at`. Research
  proposed `security/image-cve-policy.json`; the owner's example path is used.
- Unfixed UNKNOWN-severity findings are treated like MEDIUM/LOW (reported, not
  blocking) because they carry no rating; fixable UNKNOWN findings block per
  D-03.
- Secret findings of any severity block. Misconfig `FAIL` results of severity
  HIGH or CRITICAL block unless a `misconfig` policy entry covers them; lower
  misconfig results are reported.
- A report with an unsupported or unmapped OS (for example sid) or zero
  detected packages fails closed unless a `coverage` entry covers that image.
- The scan also fails if the DB `UpdatedAt` is older than 24 hours at scan
  time, and records the image's `org.opencontainers.image.revision` label.
- Base pip is upgraded from a new hash lock `requirements/bootstrap-pip.lock`
  in every python-based Dockerfile, so `pip` keeps working for learners.
- Human-readable ledger: `08-SCAN-LEDGER.md` in this phase directory, built
  from the CI evidence JSON.
- Plan split: 08-01 scanner tooling, 08-02 release gate wiring, 08-03 python
  family and postgres remediation, 08-04 SDK and native remediation plus the
  CI proof.

## Composition with Phase 7

Phase 7 (07-RESEARCH.md) adds `ARG DS60_SOURCE_REVISION` and an
`org.opencontainers.image.revision` label to the root and worker Dockerfiles,
`scripts/verify_image_revision.py`, the lifecycle harness
`scripts/check_classroom_lifecycle.py`, and a `workflow_dispatch` both-arch
qualification matrix over all 19 CI groups. Phase 8 must:

- preserve the Phase 7 ARG and LABEL lines in every Dockerfile it edits;
- record the revision label in scan evidence and reject a non-empty label that
  differs from the evidence revision;
- add the scan step to the Phase 7 dispatch workflow when it exists, and use
  that workflow for the all-groups proof run;
- use the Phase 7 lifecycle harness (when present) to show the postgres digest
  pin does not disturb retained learner volumes.

## Deferred ideas (not planned)

- Grype cross-check (not cheap enough to justify a second policy).
- Migrating to Wolfi, Chainguard, Docker Hardened Images or distroless bases.
- A scheduled weekly audit of published `latest-*` tags.
- Non-blocking scans in `verify-*-package.yml`.
- A promote-time remote rescan of candidate digests (evidence freshness is used
  instead).
- SBOM generation and image signing.
- Scanning the four GPU profiles (excluded from publication by
  `scripts/docker_release.py:171-172`).
