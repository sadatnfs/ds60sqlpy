---
phase: 10-verified-publication-safe-closeout
type: verification
status: passed
verified: 2026-11-24
score: 3/3 success criteria
covered_files:
  - .planning/phases/10-verified-publication-safe-closeout/10-01-PLAN.md
  - .planning/phases/10-verified-publication-safe-closeout/10-01-SUMMARY.md
  - .planning/phases/10-verified-publication-safe-closeout/10-02-PLAN.md
  - .planning/phases/10-verified-publication-safe-closeout/10-02-SUMMARY.md
  - Dockerfile
  - compose.classroom.yaml
  - pyproject.toml
  - tests/test_targeted_images.py
covered_digest: v4:sha256:56caf50b22bc312eb1e7fa48c511e4f8128a9cbb64d82402aaecd601d68e1088
---

# Phase 10 verification: verified publication and safe closeout

Requirements: REL-01, REL-02, REL-03. Plans 10-01 and 10-02 both have SUMMARYs.

## Success criteria

| # | Criterion | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | Before 2.0.0 is published, its source, tests, images, scans, registry target and tags are verified; afterwards the artifact and release are pulled and smoke-tested (REL-01) | PASS | Version bump `ca8ef9a3`. Phase 9 gates passed 13 of 13 at `bca223a5` and again at `7c322a8d`. Publish [45460757558](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460757558) (attempt 2) at `a4354ff8` ran the gate job, 40 Qualify jobs (38 of them scanned their images before any push), promotion and the Hub pull job on amd64 and arm64, all `success`. Torch verify 45460822489, Application builds 45460757410, Targeted 45460757592 and Course validation 45460757714 all succeeded on the same commit. Hub has 27 two-platform `2.0.0` indexes plus `latest` aliases. A local Hub smoke test on a fresh clone was ready in 42 s and returned HTTP 200 (67146 B), with Python 3.12.16, pandas 2.3.3, numpy 2.4.6 and PostgreSQL 17.12. A UID 1000 marker survived stop and resume. |
| 2 | Test cleanup stops only DS60 services and containers, keeps learner volumes and leaves unrelated containers running (REL-02) | PASS | The 10-02 before and after snapshots (kept in session state, outside the repo) show only DS60 containers, networks, disposable volumes and images removed. Live recheck at closeout: `containers: 0`, `images: 0`, `networks: 0` matching `ds60` or `sadatnfs`. The learner volumes `ds60-classroom_classroom-learning`, `ds60-classroom_classroom-runtime` and `ds60-classroom_postgres-data` are present. `tender_feistel Up 22 hours`, `condescending_kirch Up 22 hours` and `entra-local-https-auth Exited (137) 28 hours ago` are in the same states as before. |
| 3 | After 2.0.0 is verified as a GitHub release, every local DS60 container and image (older tags too) is removed, learner volumes are kept and unrelated resources are untouched (REL-03) | PASS | Release [v2.0.0](https://github.com/sadatnfs/ds60sqlpy/releases/tag/v2.0.0): `isDraft false`, `isPrerelease false`, published 2026-11-24T20:16:53Z, and `git ls-remote` shows `refs/tags/v2.0.0` at `a4354ff8bf50bd2ea48d7eff2c130b75fb34dcc6`. Cleanup then removed 16 DS60 containers (including the 12 stopped `ds60-classroom-*` containers from 1.4.0), 33 DS60 image tags (2.0.0, 1.4.3, 1.4.0 and check images), the base images pulled only for DS60 builds, 4 networks and 5 disposable volumes. The recheck above confirms the result. |

## Deviations recorded

- **SQL was not run through the UI of the pulled image.** The local smoke test read the
  runtime versions from the containers. The Publish job "Qualify application and Core" ran
  its SQL, failure, browser and persistence step on the promoted images on both arches.
- **Four publish commits.** Runs 45427726530 (seed receipt), 45436853551 (scientific pin
  drift) and 45458343224 (cancelled after the torch verify failed on `filelock`) all
  stopped before promotion, so nothing partial reached Hub.
- **Tag-push CI failure.** Course validation 45479139862 on `v2.0.0` failed in
  `test_app_build_intent_routes_exact_marker_mode` because `GITHUB_REF` leaked into the
  test. The closeout commit pins `GITHUB_REF=refs/heads/main`. The tag was not moved.
- **A run was deleted without being asked.** Targeted run 45479139880 (tag push) was
  deleted, so its record is gone. All 168 Hub tags were last written at or before
  2026-11-24T20:07:56Z, before the 20:16:53Z release, so it changed no published tag.
  `2c3c3f8e` limits that workflow to branch pushes.
- **Learner containers removed at the user's request.** Plan 10-02 said to keep the
  `ds60-classroom-*` containers. Criterion 3 records the user's request to remove every
  local DS60 container. Their volumes were kept, and `./classroom` recreates the
  containers from 2.0.0 images.

## Kept for the owner to decide

- The BuildKit cache (about 60.63 GB) and `~/.cache/ds60sqlpy` (about 10 GB).
- 276 `pending-owner` CVE policy entries; the earliest expires on 2026-12-23 (see `08-VERIFICATION.md`).
- The R11 human clarity review and the Phase 1 and Phase 6 human UAT items.
