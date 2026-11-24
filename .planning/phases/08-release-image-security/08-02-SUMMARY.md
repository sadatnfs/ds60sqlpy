---
phase: 08-release-image-security
plan: 02
subsystem: release-pipeline
status: complete
requirements: [SEC-01]
tags: [trivy, release, staging, promotion, github-actions]
requires: [08-01, 07-01]
provides: "stage --scan, staged receipt schema 2 with a scan block, promote freshness/expiry/policy re-verification, scan steps in both publication workflows"
affects: [08-03, 08-04]
files_changed:
  - scripts/docker_release.py
  - scripts/ci_release_artifacts.py
  - .github/workflows/publish-images.yml
  - .github/workflows/targeted-images.yml
  - tests/test_docker_release.py
  - tests/test_ci_release_artifacts.py
  - tests/test_ci_contract.py
  - tests/test_targeted_images.py
  - scripts/ci_hub_acceptance.py        # deviation
  - scripts/ci_hub_release_audit.py     # deviation
  - tests/test_ci_scientific_projects.py  # deviation
key-decisions:
  - "Full scan evidence travels in the always-uploaded scan-reports artifact, not the release-receipt artifact; the receipt carries a bounded summary plus evidence_sha256"
  - "Targeted build-test mode scans each local image by tag because it records no tested snapshot; publish mode scans the tested snapshot"
  - "release.json gains an optional top-level scan key; hub acceptance and audit accept it"
actuals:
  tasks: 3
  commits: 0
  tokens: 60000
---

# Phase 8 Plan 02: Release scan gate wiring Summary

`docker_release.py stage` cannot tag or push without clean, fresh, policy-bound Trivy evidence for exactly the qualified image IDs. Staged receipts are now schema 2 and carry a scan block. `promote` re-checks DB age, the policy hash and suppression expiry, then records scan evidence per promoted native digest in release.json. Both publication workflows run the scan between qualify and stage.

Commits: 0. Under the orchestrator rules (exec-rules.md) the orchestrator commits, so this plan has no plan_head_before/after ledger.

## What was built

### scripts/docker_release.py (Tasks 1 and 3)
- `stage --scan PATH` is required, so a missing flag is an argparse usage error (exit 2) before anything is tagged. The dispatcher runs `load_scan` before `qualification_records` and `stage_images`, which means it runs before any local preflight, tag or push.
- `scan_binding` validates, in order:
  - evidence `schema` 1 and kind `ds60-scan-evidence`
  - context equal to the tested snapshot
  - architecture
  - `scanner.image == image_scan.TRIVY_IMAGE` and the version
  - DB `db_updated_at` not in the future and at most 24 hours old
  - `policy_sha256` equal to the sha256 of the committed `docker/cve-policy.json`, which must also validate today through `image_scan.load_policy`
  - `passed` true (this covers the postgres reference)
  - for every tested image, exactly one evidence image with the same profile and `tested_image_id`, an empty `blocking` list, and well-formed counts, suppressed entries and report_sha256.
- The evidence file is bounded at 64 MiB. Suppressed lists are deduplicated and capped at 500 per image.
- The staged receipt is `schema_version` 2 with `scan`. The scan block holds `{evidence_sha256, scanner_image, scanner_version, db_updated_at, java_db_updated_at, policy_sha256, scanned_at, images[{profile, tested_image_id, counts, suppressed[{id, package, expires_at}], report_sha256}]}`. `staged_receipt` requires schema 2 with exact key sets, and every staged image must have a scan image with the same tested_image_id. Schema 1 receipts fail cleanly (Pitfall 10).
- `promotion_inputs(..., now=None, scans=None)` calls `promotion_scan_check` on every receipt. It rejects a DB more than 24 hours old at promote time, a policy hash that differs from the committed policy, a committed policy that no longer validates today (an expired entry), and any suppression whose `expires_at` is before promote day.
- `promote_release(..., scan=...)` checks that scan records cover exactly the selected profiles × architectures with matching native digests. It adds `report["scan"][profile][arch]`, holding tested_image_id, native_digest, counts, suppressed ids, report_sha256, evidence_sha256, scanner_image, db_updated_at, policy_sha256 and scanned_at, before the first write. The version-then-latest write order is unchanged. Recovery promotion (no natives) writes no scan key.

### scripts/ci_release_artifacts.py
- Receipts of kind `ds60-staged-images` require `schema_version` 2. Gate and scientific kinds stay at 1.

### Workflows (Tasks 1 and 2)
Four jobs now have, between `ci_classroom.py qualify` and `docker_release.py stage`: publish-images.yml `seed` and `workers`, and targeted-images.yml `seed` and `workers`. Each job gets:
1. a UTC date step (`id: scan-date`)
2. `actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9` (v6.1.0, resolved through `gh api repos/actions/cache/git/ref/tags/v6.1.0`, a commit object), with path `${{ runner.temp }}/trivy` (outside the checkout) and key `trivy-db-${{ runner.os }}-${{ runner.arch }}-<date>`
3. "Scan qualified images before any publication", which runs `set -euo pipefail`, `image_scan.py download-db --cache "$RUNNER_TEMP/trivy"`, then `image_scan.py scan --tested work/tested-images.json --policy docker/cve-policy.json --cache ... --output work/scan-evidence.json --reports work/scan-reports`. Seed jobs add `--reference "postgres=$postgres"`. The ref is read from the `DS60_POSTGRES_IMAGE` default in compose.classroom.yaml with a one-line Python regex and pulled first, so 08-03's pin flows through. The step has no `if:`, no secrets and no `DOCKERHUB_*` env. Exit 2 from `scan` fails the job.
4. an `if: always()` upload `scan-reports-seed-<arch>-attempt-<n>` or `scan-reports-<group>-<arch>-attempt-<n>`, retention 30 days
5. `--scan work/scan-evidence.json` on the stage command.

In targeted-images.yml the scan step runs in both modes. Publish mode scans the tested snapshot. Build-test mode has no gate or tested snapshot (inspect is publish-only), so it scans the postgres reference (seed only) and each local `<repository>:$RELEASE_VERSION` from `docker/classroom-images.tsv` with `--image/--profile`. Each scan writes its own `work/scan-evidence-<profile>.json`. The step scans every image and then fails if any scan failed. This is the build-test path 08-04 uses to prove remediation in CI.

Trivy runs only through `scripts/image_scan.py` (the pinned `aquasec/trivy:0.76.2@sha256:...` via docker run). No workflow uses an `aquasecurity/*` action.

### Tests
- tests/test_docker_release.py: fixtures use schema 2 with a scan block, and the profiles fixture writes the policy. New tests:
  - stage without `--scan` is a usage error and tags nothing
  - 11 parametrized evidence rejections (wrong tested_image_id, blocking findings, missing profile, architecture, revision, stale DB, policy hash, scanner image, `passed` false, and others), each asserting `docker.operations == []`
  - clean evidence writes a schema 2 receipt
  - `stage_images` refuses a scan block for other IDs
  - `staged_receipt` rejects schema 1, missing scan and mismatched scan (4 cases)
  - `promote_scan` rejects a stale DB, a changed policy, an expired policy entry and an expired suppression
  - `promote_scan` accepts fresh evidence and records it per promoted digest
- tests/test_ci_release_artifacts.py: seed document at schema 2; staged schema 1, 3, "2" and True rejected; gate receipts stay schema 1 (schema 2 rejected).
- tests/test_ci_contract.py:
  - `test_release_scan_gate_precedes_every_stage`: in every job with `docker_release.py stage`, the single scan step sits after qualify and before stage. It has no publish `if:` and no `secrets.`, it includes download-db, `$RUNNER_TEMP/trivy`, the policy flag, `--tested` and `set -euo pipefail`, and the seed scan has the postgres reference. Each job has exactly one pinned cache step before the scan with the runner.temp path, and an `always()` scan-reports upload before stage. Stage passes `--scan`, and the receipt artifacts upload only `work/release-receipt.json`. The test requires exactly 4 staging jobs.
  - `test_trivy_runs_only_through_the_pinned_image_scan_wrapper`: TRIVY_IMAGE is digest-pinned, and no workflow contains `aquasecurity/`, `aquasec/trivy`, or a single-line `run: ... trivy`.
- tests/test_targeted_images.py: accepts the new `scan-reports-*` always-upload (30 days, evidence plus reports paths) and excludes it from the single checks-report assertion.

## Verification (real output)

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-08-02 -q tests/test_docker_release.py tests/test_image_scan.py tests/test_ci_release_artifacts.py tests/test_ci_scientific_projects.py tests/test_ci_release_status.py tests/test_ci_hub_acceptance.py tests/test_ci_hub_release_audit.py tests/test_ci_contract.py tests/test_targeted_images.py tests/test_runtime_qualification_workflow.py` | Initial run: 400 passed, 3 failed. After the follow-up fixture fixes: **402 passed, 1 failed** (only the relock-python.yml contract failure, owned by 08-03 and the orchestrator; see below) |
| same, `tests/test_docker_release.py -k "scan or schema"` | 23 passed, 61 deselected |
| Plan Task 1 seed-order one-liner on publish-images.yml | `seed order ok` |
| `.venv/bin/ruff check` on the 9 touched Python files | All checks passed! |
| `.venv/bin/ruff format --check` on the same files | all formatted (test_ci_contract.py was reformatted once by `ruff format`) |
| `.venv/bin/mypy src` | Success: no issues found in 62 source files |
| `.venv/bin/mypy --strict` on the 4 touched scripts | Success: no issues found in 4 source files |
| `yaml.safe_load` on both edited workflows | yaml ok |
| `bash -n` on the 4 scan step bodies (expressions substituted) | rc 0 for all four |
| Ad hoc: hub audit `validate_receipt` with a `scan` key / extra key / list scan | accepts / rejects / rejects |
| Dash scan (perl) on all touched files and both workflows | no matches |
| `set -a; . ./.env; set +a; ./scripts/lint-repo` | "Lint checks passed." then exit 1 at the Julia formatter Docker build: Docker Hub `429 Too Many Requests` on auth.docker.io. lint-repo does not invoke actionlint, and no actionlint or shellcheck binary or image exists locally. **actionlint was not run.** |

Failures at first run and their resolution:
1. `test_ci_scientific_projects.py::test_base_import_pulls_only_four_qualified_native_digests` failed on the 07-01 revision label check because its fake inspect returned `"Labels": {}`. **Fixed in follow-up** (fixture only, deviation 8).
2. `test_ci_scientific_projects.py::test_immutable_config_readback_catches_a_tampered_import_when_old_worker_config_was_absent` failed with "Scan evidence does not cover exactly the staged image IDs" because the test changed java21's tested_image_id without changing the scan block. **Fixed in follow-up** (fixture only, deviation 8).

Still failing (orchestrator will add the branch):
3. `test_ci_contract.py::test_release_jobs_target_linux_containers_and_contributor_tooling` fails on `relock-python.yml` (an untracked workflow that 08-03 is adding, runs on `ubuntu-24.04`). The orchestrator-requested runtime-qualification.yml branch is in place and passes. 08-03 needs a matching `elif path.name == "relock-python.yml":` branch in this test (tests/test_ci_contract.py is owned by this plan, so coordinate through the orchestrator).

## Deviations from Plan

1. **[Rule 3 - Blocking] Scan evidence not in the receipt artifact.** The plan said to include `work/scan-evidence.json` in the receipt artifact path. `ci_release_artifacts.receipt_bytes` requires exactly one file per receipt artifact, promote parses every receipt file, and evidence can exceed the 256 KiB receipt bound. The evidence goes in the always-uploaded `scan-reports-*` artifact instead. The receipt binds it by `evidence_sha256`, and a contract test asserts the receipt artifact path stays `work/release-receipt.json`.
2. **[Rule 3 - Blocking] scripts/ci_hub_acceptance.py and scripts/ci_hub_release_audit.py (not in files_modified).** The plan requires `scan` in release.json, but both enforce exact key sets and would have rejected every new release right after promote. Minimal edit: accept an optional non-empty dict `scan` key. Acceptance raises "Promotion receipt scan evidence is malformed" otherwise. scripts/ci_hub_reverify.py was left alone because it validates a fixed historical release.
3. **[Rule 3 - Blocking] tests/test_ci_scientific_projects.py (not in files_modified).** Its staged receipt fixture was schema 1 with no scan. It is now schema 2 with a well-formed scan block. scripts/scientific_receipts.py needed no change because it delegates to `staged_receipt`.
4. **Targeted build-test scan mode.** The plan says the targeted scan must run in build-test mode, but `--tested` needs `work/tested-images.json`, which only exists in publish mode. The step branches on `needs.intent.outputs.mode` and uses per-image `--image/--profile` scans in build-test. Build-test evidence is not used for staging.
5. **Orchestrator request:** added the 07-03 `runtime-qualification.yml` branch from work/07-03/test_ci_contract.patch to `test_release_jobs_target_linux_containers_and_contributor_tooling`, and included tests/test_runtime_qualification_workflow.py in the final run (passes). My scan-gate test only inspects jobs that run `docker_release.py stage`, so runtime-qualification.yml is exempt.
6. **Phase 7 dispatch workflow:** `.github/workflows/runtime-qualification.yml` exists (07-03), but per orchestrator coordination this plan did not touch it, so it is **not** scan-gated. 08-04 should rely on targeted build-test pushes, which now scan, or ask 07-03's owner to add the scan step.
7. Process substitutions: `.venv/bin/python` and `--basetemp=work/test-tmp-08-02` instead of the plan's `work/test-tmp`; no commits, no actionlint (unavailable, see above); no STATE/ROADMAP/REQUIREMENTS updates (orchestrator-owned).
8. **[Follow-up, orchestrator request] Two more fixture fixes in tests/test_ci_scientific_projects.py.** No production code changed.
   - `test_base_import_pulls_only_four_qualified_native_digests`: the fake `docker image inspect` now returns the `org.opencontainers.image.revision` and `org.opencontainers.image.version` labels from the fixture context, as the 07-01 label check requires.
   - `test_immutable_config_readback_catches_a_tampered_import_when_old_worker_config_was_absent`: the test rewrites java21's `tested_image_id` to the root digest. It now applies the same change to the matching scan image before recomputing `receipt_sha256`. The scan block therefore still covers exactly the staged IDs, and the test reaches its intended "immutable native manifest" failure.
   - Ran `ruff check` (All checks passed!) and `ruff format --check` (1 file already formatted) on the file.

## Notes for 08-03
- `compose.classroom.yaml` currently has `DS60_POSTGRES_IMAGE:-postgres:17` (a tag, not a digest). The workflows read this default with the regex `DS60_POSTGRES_IMAGE:-([^}]+)`. Keep the `${DS60_POSTGRES_IMAGE:-<ref>}` form when you pin it.
- `relock-python.yml` breaks `test_release_jobs_target_linux_containers_and_contributor_tooling` until that test gets a branch for it. The test also asserts `contents: read`, pinned actions and `persist-credentials: false` for every workflow.
- Any policy change alters `policy_sha256`. Receipts staged before a policy edit cannot be promoted after it, which is intended.

## Notes for 08-04
- The CI evidence is in `scan-reports-seed-<arch>-attempt-<n>` and `scan-reports-<group>-<arch>-attempt-<n>`, kept for 30 days and uploaded even on failure.
- A targeted `[build-test-<group>]` push scans without secrets and fails on blocking findings, which proves remediation. Publication requires the same evidence, plus promote within 24 hours of the DB timestamp.
- release.json `scan[profile][arch]` ties counts and suppressed ids to each promoted native digest (Phase 8 success criterion 2).
- Size: release.json is bounded at 256 KiB in hub acceptance (MAX_REPORT), and the scientific receipt embeds 4 staged receipts inside 256 KiB. Large suppression lists (up to 500 per image) could approach these bounds. Keep the suppressions small.

## Known Stubs
None.

## Threat Flags
None beyond the plan's threat model. The scan step adds no secrets, and the cache lives under runner.temp.

## Self-Check: PASSED
All listed files exist and contain the described changes, and the verification commands above were run with the outputs shown. There are no commits to check, per orchestrator rules.
