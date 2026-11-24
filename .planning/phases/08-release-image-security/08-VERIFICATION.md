---
phase: 08-release-image-security
type: verification
status: passed
verified: 2026-11-24
score: 2/2 success criteria
covered_files:
  - .github/workflows/publish-images.yml
  - .planning/phases/08-release-image-security/08-01-PLAN.md
  - .planning/phases/08-release-image-security/08-01-SUMMARY.md
  - .planning/phases/08-release-image-security/08-02-PLAN.md
  - .planning/phases/08-release-image-security/08-02-SUMMARY.md
  - .planning/phases/08-release-image-security/08-03-PLAN.md
  - .planning/phases/08-release-image-security/08-03-SUMMARY.md
  - .planning/phases/08-release-image-security/08-04-PLAN.md
  - .planning/phases/08-release-image-security/08-04-SUMMARY.md
  - docker/cve-policy.json
  - scripts/image_scan.py
  - tests/test_image_scan.py
covered_digest: v4:sha256:0f4d4e362a0ef3243dcd67c404bd82291910b762a2b640e2b6c8048e8314e7fa
---

# Phase 8 verification: release image security

Requirement: SEC-01. Plans 08-01 to 08-04 all have SUMMARYs; 08-03 and 08-04 have
Phase 10 closure sections. Per-image results are in `08-SCAN-LEDGER.md`.

## Gate rules checked

- A fixable finding at any severity blocks and can never be placed in the policy (D-03).
- An unfixed Critical or High finding blocks unless a live, unexpired, image-scoped
  policy entry covers it (D-04, D-05). Trivy runs with `--exit-code 0`; DS60 code
  (`scripts/image_scan.py`) decides pass or fail from the full JSON.
- `python scripts/image_scan.py validate-policy` at closeout:
  `policy valid: 276 entries (276 pending-owner)`. 249 are vulnerability entries and 27
  misconfig entries; expiries run from 2026-12-23 to 2027-02-21.

## Success criteria

| # | Criterion | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | Every image meant for publication has current scan results with no unresolved CVE | PASS | Publish run 45460757558 (attempt 2) at release commit `a4354ff8` ran the "Scan qualified images before any publication" step in all 38 image-group Qualify jobs (19 groups on amd64 and arm64) before any push, and all passed. The seed job scanned app, python-core and postgres on both arches with Trivy 0.76.2: app 0 blocking (87 suppressed), python-core 0 blocking (60 suppressed), postgres 0 blocking (66 suppressed). The 2 scientific-projects jobs publish no image and have no scan step. |
| 2 | A detected CVE is remediated or rebuilt and rescanned; clean evidence names the image and candidate | PASS | Remediation commits `09f0c0cc`, `5ed195bc`, `0eed694b`, `46dc32fc`, `6be2ffd4`, `0770e8fd` and `e5ebc20a`: the Python family moved to trixie slim, gcc/go/rust/php/spark workers were slimmed, R moved off sid to `rocker/r-ver:4.6.1`, every base was digest-pinned, Spark went to 4.3.0 with re-shaded jars, torch to 2.15.0, and the locks were refreshed. Local arm64: 17 profiles, 0 fixable. CI proof: 19 `[build-test-*]` groups, each green on amd64 and arm64 (run ids and commits in the ledger). Scan evidence files record the image, revision and policy digest. |

## Open owner items (not blocking under D-14)

- All 276 policy entries still say `reviewer: pending-owner`. They need owner review
  before they expire, and the earliest expires on 2026-12-23.
- The postgres image carries libxml2 CVE-2026-6653 (Critical, no upstream fix), covered
  by a policy entry.
- Spark 4.0.1 remains in `spark-likelihood`, `spark-tmbad`, `spark-tmb`, `spark-torch`
  and `spark-deployment`. None of them is a published classroom image.
- Scientific project images are not published, so they are not scanned by the gate.
