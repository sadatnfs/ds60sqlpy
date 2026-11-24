---
phase: 10-verified-publication-safe-closeout
plan: 02
subsystem: closeout
status: complete
requirements: [REL-02]
requirements-completed: [REL-02]
tags: [docker, cleanup, closeout, learner-data]
requires: [10-01]
provides:
  - before and after Docker snapshots for the closeout
  - a machine with no DS60 containers, networks or image tags and every learner volume kept
affects: []
key-files:
  created:
    - .planning/phases/10-verified-publication-safe-closeout/10-02-SUMMARY.md
  modified: []
decisions:
  - The user asked to remove all local DS60 Docker images and containers once the release was green, which overrides plan task 3 for the ds60-classroom containers. Learner volumes were still kept.
  - Unrelated containers (the awesome-copilot MCP servers, entra-local-https-auth) and non-DS60 volumes were not touched.
  - The BuildKit cache and ~/.cache/ds60sqlpy were kept and reported instead of pruned.
commits: [Phase 10 closeout commit]
actuals:
  tasks: 5
  commits: 1
completed: 2026-11-24
---

# Phase 10 Plan 02: safe closeout Summary

No DS60 container, network or image tag is left on the machine, every learner volume is kept
and no unrelated container was touched (REL-02 PASS, with one user-directed deviation).

Snapshots: `~/.copilot/session-state/38e18817-b839-4a99-b157-b1b6a4fb4916/files/p10-cleanup/{before,after}-{ps,images,volumes,networks}.txt`
(outside the repository, because they list unrelated local containers).

## Before and after

| Resource | Before | After | Removed |
| --- | --- | --- | --- |
| Containers (`docker ps -a`) | 41 | 29 | 16 DS60 containers; 4 unrelated MCP containers started in between |
| Images (`docker image ls`) | 80 | 34 | 33 DS60 tags plus the base images pulled for DS60 builds |
| Volumes | 22 | 17 | 5 disposable DS60 volumes |
| Networks | 8 | 4 | 4 DS60 networks |

### Removed

- Containers: 4 `ds60-p10-smoke-*` (lab, python-core worker, postgres, classroom-init) and 12
  `ds60-classroom-*` (lab, postgres, classroom-init and 9 workers). All 12 had been stopped
  for 4 to 5 days and ran the old 1.4.0 lab and worker images, `postgres:17` or untagged
  local worker builds.
- Volumes: `ds60-p10-smoke_classroom-learning`, `ds60-p10-smoke_classroom-runtime`,
  `ds60-p10-smoke_postgres-data`, `ds60-p8-scan-token-0a15c596`, `ds60-p8-scan-token-c505df6e`
- Networks: `ds60-classroom_default`, `ds60-classroom_module-private`,
  `ds60-p10-smoke_default`, `ds60-p10-smoke_module-private`
- DS60 images (33 tags): the 3 pulled `sadatnfs/ds60sqlpy` 2.0.0 tags and 4 untagged
  `sadatnfs/ds60sqlpy` layers left by local builds, the `ds60sqlpy-lab`,
  `ds60sqlpy-worker-python-core` and `ds60sqlpy-postgres` 1.4.0 and 1.4.3 builds, the
  `ds60-p10-*`, `ds60-p7-torch-check`, `ds60-p8-julia-check` and `ds60-p5-ref-*` check images
  and 9 `ds60-formatting*` images
- Base images pulled only for DS60 builds, for example `eclipse-temurin:21-jdk-jammy`,
  `gcc:14.3.0-bookworm`, `julia:1.11`, `swift:6.3.3-noble`, `rust:1.99.1-bookworm` and
  `mcr.microsoft.com/playwright/python:v1.64.1-noble`
- Scratch: `work/` went from 27087 MB to 1357 MB. `~/.cache/ds60sqlpy/diag` did not exist.

### Kept

- Learner volumes: `ds60-classroom_classroom-learning`, `ds60-classroom_classroom-runtime`,
  `ds60-classroom_postgres-data`
- Every non-DS60 container, including `tender_feistel`, `condescending_kirch`, the other
  `awesome-copilot` MCP servers and `entra-local-https-auth`, and every non-DS60 volume
- The BuildKit cache (about 60.63 GB) and `~/.cache/ds60sqlpy` (10 GB: browser, Trivy, uv and
  wheel caches), reported for the user to prune if wanted

## Recheck after the closeout

`docker ps -a` lists 0 DS60 containers, `docker image ls` lists 0 DS60 or `sadatnfs` tags,
`docker network ls` lists 0 DS60 networks, and `docker volume ls` still lists the three
`ds60-classroom_*` learner volumes. `tender_feistel` and `condescending_kirch` are running, and
`entra-local-https-auth` is still in the `Exited (137)` state it was in before the cleanup.

## Deviations

- **The 12 `ds60-classroom-*` containers were removed** although plan task 3 said never to
  remove them. The user asked for all local DS60 images and containers to be cleaned up once
  the release was green, and ROADMAP Phase 10 criterion 3 records that request. The
  containers had been stopped for days and their volumes were kept, so learner work, notes
  and the database survive. The next `./classroom` start recreates the containers from 2.0.0
  images.
- **The local 1.4.0 and 1.4.3 learner images were removed** for the same reason. They are
  superseded by 2.0.0 on Docker Hub.
- **Named disposable projects were already gone.** `ds60-phase1-browser`,
  `ds60-phase6-browser`, `ds60-phase9-browser` and `ds60-livetest-pg` were not in the before
  snapshot, so there was nothing to remove for them.
- Later closeout test runs recreated pytest scratch under `work/test-tmp-p10*`. It is deleted
  with the closeout commit.

## Self-Check: PASSED
