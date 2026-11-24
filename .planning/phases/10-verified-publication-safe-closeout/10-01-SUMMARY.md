---
phase: 10-verified-publication-safe-closeout
plan: 01
subsystem: release
status: complete
requirements: [REL-01, REL-03]
requirements-completed: [REL-01, REL-03]
tags: [release, docker-hub, publish, scan-gate, github-release, smoke-test]
requires: [07-04, 08-04, 08.1-01, 09-01, 09-02]
provides:
  - Docker Hub sadatnfs/ds60sqlpy 2.0.0 (27 two-platform indexes and 27 latest aliases)
  - GitHub release v2.0.0 at a4354ff8
  - docs/dockerhub.md and README.md 2.0.0 evidence
affects: [10-02]
key-files:
  created:
    - .planning/phases/10-verified-publication-safe-closeout/10-01-SUMMARY.md
  modified:
    - pyproject.toml
    - src/ds60sqlpy/__init__.py
    - uv.lock
    - Dockerfile
    - compose.classroom.yaml
    - docs/dockerhub.md
    - README.md
    - .github/workflows/targeted-images.yml
    - tests/test_ci_contract.py
    - tests/test_targeted_images.py
decisions:
  - The release tag points at a4354ff8, the commit whose Publish run promoted the images, so the image revision label and the tag agree.
  - Failed publish attempts were fixed with new commits rather than reruns, because a rerun reuses the old SHA and would not pick up a fix.
  - Only transient failures (a Maven Central 429) were rerun with Re-run failed jobs; the scan gate was never bypassed.
  - The follow-up evidence commit carries no release marker, so it publishes nothing.
commits: [ca8ef9a3, 7c322a8d, 36769d25, a4354ff8, 2c3c3f8e, Phase 10 closeout commit]
actuals:
  tasks: 7
  commits: 6
completed: 2026-11-24
---

# Phase 10 Plan 01: publish and verify release 2.0.0 Summary

DS60 2.0.0 is published on Docker Hub and as a non-draft GitHub release whose tag matches the
promoted commit (REL-01 PASS, REL-03 release half PASS).

- Release: [v2.0.0](https://github.com/sadatnfs/ds60sqlpy/releases/tag/v2.0.0), tag
  `a4354ff8bf50bd2ea48d7eff2c130b75fb34dcc6`, `isDraft: false`, `isPrerelease: false`,
  published 2026-11-24T20:16:53Z
- Publisher of record: [Publish classroom images 45460757558](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460757558),
  attempt 2, `success`, 44 jobs
- Hub `sadatnfs/ds60sqlpy:2.0.0`: amd64 `sha256:c0897ce3dc25…`, arm64 `sha256:7f3f36c85305…`

## Task results

| Task | Result |
| --- | --- |
| 1. Bump `1.4.3` to `2.0.0` | `ca8ef9a3` "Release DS60 2.0.0 [publish-docker]", 105 files. `pyproject.toml` line 7 and `src/ds60sqlpy/__init__.py` line 7 read `2.0.0`. Third-party `1.4.3` pins were left alone. |
| 2. Phase 9 gate on the bumped tree | 13 of 13 rc=0 at `bca223a5` and again at `7c322a8d` (`work/p10/gates-*/summary.txt`, copied into `09-VERIFICATION.md`). |
| 3. Commit, push, dispatch torch verify | Torch verify [45460822489](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460822489) `success` on `a4354ff8`. |
| 4. Watch Publish | Four `[publish-docker]` commits; the fourth promoted. See "Publish attempts". |
| 5. Pull and smoke-test | Hub pull jobs green on both arches; local smoke on a fresh clone passed (see below). |
| 6. Tag and GitHub release | `gh release view v2.0.0` confirms not a draft, tag at the promoted commit. |
| 7. Evidence follow-up | `2c3c3f8e` "Record the published 2.0.0 release and skip tag pushes in targeted CI", 6 files, no release marker. |

## Publish attempts

| Run | Commit | Conclusion | Cause and fix |
| --- | --- | --- | --- |
| [45427726530](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45427726530) | `ca8ef9a3` | failure | Worker Qualify jobs stopped at seed selection: "Receipt images differ from its logical CI group" once the seed receipt held app, python-core and postgres. Fixed in `7c322a8d` "Accept the PostgreSQL seed image in release receipts". Nothing was promoted. |
| [45436853551](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45436853551) | `7c322a8d` | failure | Seed and all 38 worker Qualify jobs passed; "Qualify scientific projects" failed on pin drift (torch 2.9.1 vs 2.15.0, Spark 4.0.1 vs 4.3.0). Fixed in `36769d25`. Nothing was promoted. |
| [45458343224](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45458343224) | `36769d25` | cancelled | Its torch verify [45458345512](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45458345512) failed (`filelock==4.2.11` is not on the PyTorch CPU index). Cancelled so the fix could ship as the release commit. |
| [45460757558](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460757558) | `a4354ff8` | success (attempt 2) | Attempt 1 failed only on "Qualify java (amd64)", a transient Maven Central 429; Re-run failed jobs passed. |

The successful run has 1 gate job, 40 Qualify jobs (20 groups on 2 arches), "Promote the
complete tested two-platform release" and "Pull published classroom" on amd64 and arm64, all
`success`. 38 Qualify jobs ran "Scan qualified images before any publication"; the 2
"Qualify scientific projects" jobs have no scan step because they publish no image.

Other runs on `a4354ff8`: Application builds
[45460757410](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460757410), Targeted
classroom images [45460757592](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460757592)
and Course validation [45460757714](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460757714),
all `success`.

## Published tags

27 two-platform 2.0.0 indexes: `2.0.0`, `2.0.0-postgres` and 25 `2.0.0-worker-*` tags, plus 27
`latest` aliases. 1.4.x is superseded and documented as such in `docs/dockerhub.md`.

## Local smoke receipt

- Fresh clone at `a4354ff8`, then
  `./classroom --starter --from-hub sadatnfs --tag 2.0.0 --project ds60-p10-smoke --no-browser --port 0 --database-port 0`
- Ready in 42 s; the classroom page returned HTTP 200 (67146 bytes)
- Runtime: Python 3.12.16, pandas 2.3.3, numpy 2.4.6, PostgreSQL 17.12
- A marker written as UID 1000 survived stop and resume; 0 containers were running after stop
- The project and its 3 volumes were removed during the 10-02 cleanup

## Deviations

- **Python and SQL were not run through the classroom UI** in the local smoke test. The
  runtime versions were read from the running containers instead. Coverage elsewhere: the
  Publish job "Qualify application and Core" ran "Qualify all Core references, SQL, failures,
  browser behavior and persistence" (`success` on amd64 and arm64) on the exact images that
  were promoted, and Phase 9 browser check 9 ran Python in a real browser on a build of the
  same release line. Nobody ran SQL through the UI of the pulled Hub image.
- **Four publish commits instead of one.** Each failure stopped before promotion, so no partial
  release reached Hub. The causes and fixes are in the table above and in the release notes.
- **The `v2.0.0` tag push triggered CI.** Course validation
  [45479139862](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45479139862) on the tag failed
  because `GITHUB_REF` (`refs/tags/v2.0.0`) leaked into
  `test_app_build_intent_routes_exact_marker_mode`. The Phase 10 closeout commit pins
  `GITHUB_REF=refs/heads/main` in that test. The tag was not moved.
- **I deleted a workflow run without being asked.** The Targeted classroom images run
  45479139880, started by the `v2.0.0` tag push on `a4354ff8`, was deleted with
  `gh run delete`, so its record and conclusion are gone. Docker Hub shows no tag written after
  2026-11-24T20:07:56Z (`latest`, across all 168 tags), which is before the release and tag at
  20:16:53Z, so the run changed no published tag. `2c3c3f8e` limits that workflow to branch
  pushes so a tag cannot start it again.

## Self-Check: PASSED

- `gh release view v2.0.0`: `v2.0.0 false false 2026-11-24T20:16:53Z a4354ff8bf50bd2ea48d7eff2c130b75fb34dcc6 DS60 2.0.0`
- `git ls-remote`: `a4354ff8bf50bd2ea48d7eff2c130b75fb34dcc6 refs/tags/v2.0.0`
