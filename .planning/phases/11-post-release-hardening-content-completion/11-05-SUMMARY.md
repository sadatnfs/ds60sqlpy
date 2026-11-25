---
phase: 11-post-release-hardening-content-completion
plan: 05
subsystem: release
status: complete
requirements: [HARD-05]
requirements-completed: [HARD-05]
tags: [docker-hub, scientific-projects, image-scan, multi-arch, release-metadata]
requires: []
provides:
  - scan-gated candidate tags for the qualified spark-torch and spark-tmb images on both architectures
  - VERSION-project-* multi-arch indexes and latest-project-* aliases written only by the full publication workflow
  - a scientific section in release.json with index digests, native digests and scan records
  - AMD64 Hub acceptance that inspects every published scientific index against the receipt
affects: [11-08]
key-files:
  created:
    - .planning/phases/11-post-release-hardening-content-completion/11-05-SUMMARY.md
  modified:
    - .github/workflows/publish-images.yml
    - scripts/ci_scientific_projects.py
    - scripts/scientific_receipts.py
    - scripts/docker_release.py
    - scripts/ci_hub_acceptance.py
    - scripts/ci_hub_release_audit.py
    - scripts/image_scan.py
    - README.md
    - "docs/{dockerhub,dependency-profiles,validation}.md"
    - "tests/{test_ci_scientific_projects,test_docker_release,test_ci_hub_acceptance,test_ci_hub_release_audit,test_image_publication}.py"
decisions:
  - Each architecture job scans its qualified project images without registry credentials and pushes them only to per-run candidate tags. Promotion, not the build job, joins AMD64 and ARM64 into one index per project.
  - The scan uses the same pinned scanner and docker/cve-policy.json as the course images. A policy entry for a qualified base image also covers the same finding in the project image built on it (SCIENTIFIC_PROFILES).
  - The tmb-public-api and tmb-cpp-api indexes reference the same native images as project-spark-tmb, because both APIs are qualified inside the Spark/TMB image. Each index keeps its own project annotation and digest.
  - The launcher (--all, --profile, --from-hub) never selects these tags, and the manual publisher and the targeted workflow never write them.
  - A rerun for the same version and revision reuses an already-published scientific index, because rebuilt project images cannot reproduce the earlier digests.
commits: [ff483b2c, 87af270e]
actuals:
  tasks: 4
  commits: 2
completed: 2026-11-24
---

# Phase 11 Plan 05: publish the scientific project images from GitHub Actions Summary

The four qualified scientific images now publish only through `publish-images.yml`, and only
after a scan clean under the committed CVE policy. They appear as `VERSION-project-spark-torch`,
`-spark-tmb`, `-tmb-public-api` and `-tmb-cpp-api` multi-arch indexes with `latest-project-*`
aliases (HARD-05). The implementation landed in ff483b2c. The first real publish run and the
`docker buildx imagetools inspect` of both architectures are verified in plan 11-08.

## Workflow (publish-images.yml, scientific-projects job)

After each architecture job builds and qualifies spark-torch and spark-tmb, the workflow (+43
lines) adds four steps:

1. Records the qualified image IDs before any publication (`ci_scientific_projects.py tested`).
2. Caches the scanner DB by date, then runs `image_scan.py download-db` and `scan` against
   `work/scientific/tested-images.json` and `docker/cve-policy.json`.
3. Uploads the scan reports as an artifact kept for 30 days.
4. Stages only the scanned and qualified image IDs (`ci_scientific_projects.py stage --scan`) with
   a credentialed `DOCKER_CONFIG` removed by a logout trap. Candidate tags look like
   `ci-SHA-RUN-ATTEMPT-project-spark-torch-arm64`.

`scripts/ci_scientific_projects.py` (+106) gains the `tested` and `stage` subcommands, and
`scripts/scientific_receipts.py` (+80) records each candidate tag, native digest and scan record
in the source-bound receipt. Plan 11-01's commit 87af270e added `SCIENTIFIC_PROFILES` to
`scripts/image_scan.py`. That map lets the project images be scanned and lets a reviewed entry
for a base image also cover the project image built on it.

## Promotion and metadata (docker_release.py)

`scripts/docker_release.py` (272 lines changed) adds `SCIENTIFIC_RELEASES` for the four projects
and builds one OCI index per project at promotion. Before any write, it checks that:

- each candidate still has its recorded digest;
- the scan DB is less than 24 hours old;
- the scan policy matches the committed one.

The publication order is:

1. Worker version tags, then scientific version tags, then the app version tag.
2. The latest aliases in the same order, with the app `latest` pointer moving last.

A downgrade-protected release skips every latest alias. `release.json` gains a `scientific`
section, with each version and alias row, its index digest, the AMD64 and ARM64 native digests
and the scan records. The final receipt size is checked against the 256 KiB bound before any tag
is written. `scripts/ci_hub_acceptance.py` (+72) inspects every scientific index in the AMD64
acceptance job. `scripts/ci_hub_release_audit.py` expects the `scientific` key for releases that
record it.

## Docs

`docs/dockerhub.md` (+61) adds a "Scientific project images" section with the tag table, pull
examples and the promotion steps. It notes that releases through 2.0.0 predate these tags.
`README.md`, `docs/dependency-profiles.md` and `docs/validation.md` link to that section, and
their reference pages were regenerated.

## Verification

- Scan-gated staging, without a registry: covered by `tests/test_ci_scientific_projects.py`
  (6 new tests), including:
  - `test_stage_pushes_only_scanned_qualified_project_images_once`;
  - `test_stage_refuses_blocking_or_changed_images_before_any_push`;
  - `test_workflow_scans_scientific_images_before_a_credentialed_stage`.
- Promotion order, rerun reuse, refusal and size bound: covered by `tests/test_docker_release.py`
  (4 new tests), including:
  - `test_scientific_indexes_publish_after_workers_and_before_each_app_pointer`;
  - `test_scientific_rerun_reuses_the_published_indexes_of_this_revision`;
  - `test_scientific_release_metadata_size_is_checked_before_any_tag`;
  - `test_scientific_promotion_rechecks_scan_freshness_and_candidates`.
- Index inspection: covered by `tests/test_ci_hub_acceptance.py` (3 new tests, including
  `test_full_amd64_inspects_each_scientific_project_index`) and one new test in
  `tests/test_ci_hub_release_audit.py`.
- Publish run, `imagetools inspect` of both architectures, and no push from a local machine:
  not run in this plan. Verified in plan 11-08.

## Deviations

- **Index built at promotion.** Task 1 placed the AMD64/ARM64 manifest step in
  `ci_scientific_projects.py`. The architecture jobs only stage per-arch candidates, and
  `docker_release.py` builds the multi-arch index during promotion, after both receipts and all
  required checks succeed.
- **Scanner profile change in another commit.** The `SCIENTIFIC_PROFILES` change to
  `scripts/image_scan.py` landed in plan 11-01's commit 87af270e, not in ff483b2c.

## Self-Check: PASSED

Tasks 1 to 4 map to ff483b2c, with the scanner profile change in 87af270e. The publish-run
verification is deferred to plan 11-08.
