---
phase: 08-release-image-security
plan: 01
subsystem: release-image-security
status: complete
requirements: [SEC-01]
tags: [trivy, cve, policy, release-gate]
requires: []
provides:
  - scripts/image_scan.py (download-db, scan, validate-policy, propose-entries)
  - docker/cve-policy.json (schema 1, no entries)
  - scan evidence JSON format (kind ds60-scan-evidence) for 08-02
affects: [08-02, 08-03, 08-04]
tech-stack:
  added: ["aquasec/trivy:0.76.2@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb (container, via docker run)"]
  patterns: [stdlib CLI in docker_release.py style, injected Runner seam for offline tests]
key-files:
  created:
    - scripts/image_scan.py
    - docker/cve-policy.json
    - tests/test_image_scan.py
    - tests/fixtures/trivy/clean.json
    - tests/fixtures/trivy/fixable.json
    - tests/fixtures/trivy/unfixed.json
    - tests/fixtures/trivy/unsupported-os.json
    - tests/fixtures/trivy/rustbinary.json
    - tests/fixtures/trivy/secret-misconfig.json
    - tests/fixtures/trivy/version.json
  modified:
    - Makefile
    - docs/validation.md
decisions:
  - Freshness (24 h) applies to the vulnerability DB UpdatedAt; the Java DB must be present and is recorded but follows its own multi-day upstream cadence.
  - Trivy scans the resolved image ID (sha256:...), never the tag, in both single-image and --tested modes.
  - Misconfig policy entries match (check ID, target path, profile); coverage entries use id unsupported-os, os-not-detected or no-packages with package set to the OS label.
  - propose-entries also drafts misconfig and coverage entries, never fixable, secret, stale-db or revision findings.
metrics:
  duration: about 20 minutes
  completed: 2026-11-24
actuals:
  tasks: 3
  commits: 0
  note: orchestrator owns commits (exec-rules forbid git add/commit)
---

# Phase 8 Plan 01: Image scan gate Summary

Digest-pinned Trivy 0.76.2 run only via `docker run`, a DS60-owned
`docker/cve-policy.json`, and a stdlib Python gate that turns full Trivy JSON
into a pass/fail verdict plus evidence bound to each image ID, the scanner
digest, DB timestamps and the policy hash. Real local scan: the 1.4.3 app
image is blocked by 321 findings (168 fixable).

## What was built

- `scripts/image_scan.py`
  - `trivy_argv`: `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro -v <cache>:/root/.cache/trivy <TRIVY_IMAGE> image --image-src docker --scanners <s> --format json --exit-code 0 --skip-db-update --skip-java-db-update --quiet <image-id>`.
    The cache defaults to `~/.cache/ds60sqlpy/trivy` and is refused inside the repo.
  - `evaluate`: implements D-03 (any FixedVersion blocks as `fixable`, at any severity, and a policy entry cannot suppress it), D-04 (unfixed CRITICAL/HIGH blocks as `unaccepted` unless an exact live entry matches; unfixed MEDIUM/LOW/UNKNOWN reported), D-06 (secrets always block; misconfig FAIL HIGH/CRITICAL blocks as `misconfig` unless accepted; lower misconfig reported), the coverage rule (Debian/Ubuntu OS name not numeric such as `forky/sid`, `EOSL`, no os-pkgs result, OS not detected, or zero packages blocks as `coverage` unless a coverage entry exists), stale DB (more than 24 h blocks every image as `stale-db`) and the postgres reference rule (only fixable CRITICAL/HIGH block).
  - `load_policy` / `policy_problems`: exact key set, schema 1, kinds, exact advisory/check id regex, no wildcards, known profiles (non-GPU catalog plus `postgres`), ISO dates, not expired, at most 90 days, `reviewed_at` not in the future, non-empty justification and reviewer, no duplicate (id, package, image). `pending-owner` is accepted.
  - `scan`: `--image REF --profile NAME`, or `--tested work/tested-images.json` (exact `load_tested` shape check, scans each `tested_image_id`, copies `context` and `architecture`, enforces the image architecture and the `org.opencontainers.image.revision` rule), plus repeatable `--reference postgres=REF`. Writes raw reports to `--reports/<profile>.json` and evidence to `--output`. Exit 2 when anything blocks.
  - `download-db` (`--download-db-only` and `--download-java-db-only`), `validate-policy`, `propose-entries --evidence F --days N` (prints JSON, never writes the policy).
- Evidence keys: `schema`, `kind`, `context`, `architecture`, `scanner` (`image`, `version`, `db_updated_at`, `java_db_updated_at`), `policy_sha256`, `scanned_at`, `passed`, `unused_policy_entries`, `images[]` (`profile`, `tested_image_id`, `revision_label`, `reference`, `scanners`, `counts`, `blocking`, `suppressed`, `reported`, `report_sha256`). Each finding item has `id`, `kind`, `package`, `installed`, `fixed`, `severity`, `target`, `reason`; suppressed items add `expires_at` and `reviewer`.
- `docker/cve-policy.json`: `{"schema": 1, "entries": []}`.
- Fixtures trimmed from real 2026-11-24 reports (lab 1.4.3 probe, r-base sid, Chainguard python). The secret result in `secret-misconfig.json` is synthetic and redacted because no real secret was found in any scanned image.
- `make scan` (`IMAGE ?= ds60sqlpy-lab:1.4.3`, `PROFILE ?= app`), listed in `help`.
- `docs/validation.md`: new "Image vulnerability scans" section before "Release decision".

## Verification (real results)

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-08-01 -q tests/test_image_scan.py` | 69 passed |
| same with `-k` policy / unresolved / fixed_version / coverage / secret / freshness / revision / reference | 32 / 3 / 2 / 6 / 2 / 3 / 10 / 5 passed |
| `pytest ... tests/test_ci_contract.py tests/test_image_scan.py` | 82 passed |
| `.venv/bin/python scripts/image_scan.py validate-policy --policy docker/cve-policy.json` | `policy valid: 0 entries (0 pending-owner)`, exit 0 |
| `.venv/bin/python scripts/image_scan.py download-db` | `Trivy 0.76.2 DB 2026-11-24T01:05:31Z, Java DB 2026-11-24T00:59:05Z`, exit 0 |
| `scan --image ds60sqlpy-lab:1.4.3 --profile app --output work/p8-scan/lab-1.4.3.json --reports work/p8-scan/reports` | exit 2: `FAIL app sha256:42a928f2fff8 [C13 H184 M252 L202 U22] blocking 321 (fixable 168, misconfig 32, unaccepted 121), suppressed 0, reported 653`; pillow present in blocking (plan check printed `321 blocking`) |
| `make scan` | same verdict, evidence `work/p8-scan/app.json`, make exits with Error 2 |
| `scan --reference postgres=postgres:17 --output work/p8-scan/postgres.json` | exit 2: `FAIL postgres sha256:b60e90042aa6 [C2 H154 M210 L172 U26] blocking 83 (fixable 83), reported 481` |
| `propose-entries --evidence work/p8-scan/lab-1.4.3.json` | 153 drafted entries (121 vulnerability, 32 misconfig); 168 fixable refused |
| `.venv/bin/ruff check` / `ruff format --check` / `mypy` on the new script and test | all clean |
| `./scripts/lint-repo` (with `.env`) | `Lint checks passed.` exit 0 (one earlier run failed on other agents' in-flight files and passed on rerun) |
| Dash check on all written files (perl and the plan's python3 check) | no matches |

Lab 1.4.3 evidence details: image ID
`sha256:42a928f2fff807948d30e7841c5de4a7e7e8bac30084be5f887e1b03d9ff7d6d`,
arm64, revision label empty (pre Phase 7 image), policy sha256
`1e75888d7769cfa78b8e0ace79d5f9167ef538f648847e9e2537b40a3a4892ec`.
Fixable by package: pillow 43, virtualenv 19, filelock 12, tornado 10, zip 10,
rustls 8, pip 6, urllib3 6, astral-tokio-tar 6, rustls-webpki 6, sqlparse 5,
jupyterlab 4, setuptools 4, soupsieve 4, uv 4, rand 4, anyio 3, certifi 2,
msgpack 2, notebook 2, quinn-proto 2, rkyv 2, tar 2, jupyter_server 1,
nbconvert 1 (C11 H65 M67 L25). Unaccepted unfixed Debian 12 findings: 2
CRITICAL, 119 HIGH. Misconfig HIGH: 31 x DS-0002 (root user) in course and
worker Dockerfiles copied into `/opt/course`, 1 x KSV-0056 in
`courses/spark-deployment/projects/cluster-lab/kubernetes/access.yaml`. No
secrets found.

Postgres 17 blocking (fixable CRITICAL/HIGH): Go `stdlib` in gosu (1 CRITICAL,
25 HIGH), krb5 libraries (4 x 14 HIGH), zlib1g (1 HIGH).

### Scanner digest verification (T-08-01)

```
$ docker buildx imagetools inspect aquasec/trivy:0.76.2
Name:      docker.io/aquasec/trivy:0.76.2
MediaType: application/vnd.oci.image.index.v1+json
Digest:    sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb
  (linux/amd64 sha256:6fa071ef..., linux/arm64 sha256:6e878e51..., s390x, ppc64le)
$ docker image inspect aquasec/trivy:0.76.2 --format '{{json .RepoDigests}} {{.Created}}'
["aquasec/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"] 2026-11-05T12:48:01.084514517Z
$ gh release view v0.76.2 --repo aquasecurity/trivy --json tagName,publishedAt,isDraft,isPrerelease
{"isDraft":false,"isPrerelease":false,"publishedAt":"2026-11-05T12:50:25Z","tagName":"v0.76.2"}
$ trivy version --format json   (via the pinned container)
{"Version":"0.76.2", "VulnerabilityDB":{"UpdatedAt":"2026-11-24T01:05:31Z",...}, "JavaDB":{"UpdatedAt":"2026-11-24T00:59:05Z",...}}
```

The upstream index digest equals the pinned constant, the release exists and
was published 2026-11-05, not in the 2026-03-19 compromise window. Trivy was
never installed on the host.

## Deviations from Plan

1. **[Rule 2] Extra evidence fields.** Added `passed`, `reference` and `scanners` per image and top-level `unused_policy_entries` (the latter was in the plan text). 08-02 should rely on `passed` and per-image `blocking`.
2. **[Rule 2] Architecture and image-ID binding.** `scan` fails if an image's architecture differs from the snapshot (or the first image), or if a `sha256:` reference resolves to a different ID.
3. **Freshness scope.** Only the vulnerability DB is held to 24 h; the Java DB must exist (else `ScanError`) and is recorded. Upstream publishes the Java DB on a multi-day cadence, so a 24 h rule would fail constantly.
4. **propose-entries scope.** Also drafts `misconfig` and `coverage` entries (both policy-acceptable kinds); still refuses fixable, secret, stale-db and revision findings.
5. **Per-commit protocol not followed.** exec-rules forbid git add/commit; the orchestrator commits. No `commits`/`plan_head_*` measured.
6. **Synthetic secret fixture.** See above; it is marked synthetic here.
7. **Verify commands used `.venv/bin/python`** instead of `python`, and basetemp `work/test-tmp-08-01` (orchestrator rule).

## Pre-existing issues seen (not fixed, other agents' files)

- `ruff check src scripts tests`: 4 errors in `scripts/check_walkthroughs.py` (B023), `scripts/verify_image_revision.py`, `tests/test_image_revision.py` (E501).
- `ruff format --check`: 2 files from the in-flight Phase 7 revision verifier would be reformatted.
- `mypy src`: `src/ds60sqlpy/walkthroughs.py:191` assignment type error.
- `scripts/scan_secrets.py` flags `.env` and other agents' `work/test-tmp-*` files.

## Known Stubs

None. `docker/cve-policy.json` is intentionally empty; entries come from 08-03/08-04 after remediation.

## Threat Flags

None beyond the plan's threat model (the socket mount is read-only; no credentials are passed).

## What later plans need

- **08-02 (gate wiring):** run `python scripts/image_scan.py download-db --cache <actions/cache path>` then `scan --tested work/tested-images.json --output work/scan-evidence.json --reports work/scan-reports` between `qualify` and `stage` (add `--reference postgres=postgres@sha256:...` where the seed job scans it). Exit 2 fails the job. `stage` should require `evidence.passed`, a matching `tested_image_id` per profile, and record `policy_sha256` and `scanner.db_updated_at`; `promote` re-checks DB age at most 24 h and that the policy hash and expiries still hold. The cache path must be outside the checkout (the tool refuses otherwise); in CI use e.g. `$RUNNER_TEMP/trivy` or `~/.cache/ds60sqlpy/trivy`. Add a contract test forbidding `aquasecurity/*` actions.
- **08-03 (python family, postgres):** the 168 fixable lab findings above (re-lock uv.lock, uv >= 0.13.4 clears the rust crates, base pip). The 32 HIGH misconfig failures come from course/worker Dockerfiles and one K8s manifest shipped in `/opt/course`; either fix them (non-root USER), add `misconfig` policy entries (drafts in `propose-entries` output), or change what the app image copies. Trixie should reduce the 121 unaccepted Debian findings; remaining ones need `pending-owner` entries. Postgres needs a newer digest that fixes gosu stdlib, krb5 and zlib1g.
- **08-04 (SDK workers, R):** R on sid will block as `coverage` (`unsupported-os`, package `debian forky/sid`) until moved or given a coverage entry. Scan each worker with `make scan IMAGE=<tag> PROFILE=<profile>`.

## Self-Check: PASSED

All created files exist; tests, policy validation, the real lab and postgres scans and lint-repo were run as recorded above. No commits were made (orchestrator-owned).
