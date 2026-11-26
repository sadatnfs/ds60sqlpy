---
phase: 11-post-release-hardening-content-completion
plan: 09
subsystem: release
status: complete
requirements: [HARD-01, HARD-04, HARD-05]
requirements-completed: [HARD-01, HARD-04, HARD-05]
tags: [release, docker, cve-policy, r, swift, amazon-linux, debian]
requires: [11-08]
provides:
  - a Swift worker on the official Amazon Linux 2023 image with 0 vulnerabilities
  - R 4.6.1 built from the checksummed upstream tarball on Debian 13, with cairo built from source without X11
  - tmb-local and Spark/TMB project images rebuilt on the new R image with no fixable findings
  - a CVE policy cut from 256 to 94 pending-owner entries
  - DS60 2.1.1 published from GitHub Actions as 31 multi-arch version tags plus 31 matching latest aliases on Docker Hub and GitHub release v2.1.1 marked Latest
affects: []
key-files:
  created:
    - .planning/phases/11-post-release-hardening-content-completion/11-09-SUMMARY.md
  modified:
    - docker/workers/Dockerfile.swift
    - docker/workers/Dockerfile.r
    - src/ds60sqlpy/worker_figures.R
    - src/ds60sqlpy/secret_scan.py
    - docker/cve-policy.json
    - courses/tmb-modeling/projects/tmb-local/Dockerfile
    - courses/advanced-spark-modeling/projects/spark-tmb/Dockerfile
    - "courses/swift/authoring/answers.py and five Swift solution files (platform-dependent output)"
    - "VERSION and the 2.1.1 bump set (125 files in 15e28332)"
    - "README.md and docs/dockerhub.md (2.1.1 evidence)"
decisions:
  - Swift moved to the official swift:6.3.3-amazonlinux2023 image instead of Ubuntu Noble, which removes every Ubuntu kernel-header finding.
  - R is compiled from the checksummed 4.6.1 tarball on Debian 13 in four stages; headers stay in the builder stage and the runtime keeps gcc, g++ and gfortran for package builds (HARD-04).
  - cairo 1.18.6 is built from source without xlib or xcb, so R bitmap devices default to cairo everywhere.
  - The Amazon Linux system python3 (3.9) stays for dnf; a /usr/local/bin link makes every python3 on PATH the worker's 3.12.
  - Unfixable findings stay pending-owner entries with expiry dates; nothing is dismissed.
commits: [15e28332, 13b2ace2, 954ab255, 9d8ab4d4, c45a7170, 2fa88aac, 658d0cea, a2285ec3]
actuals:
  tasks: 4
  commits: 8
completed: 2026-11-25
---

# Phase 11 Plan 09: Minimal-CVE R and Swift bases, release 2.1.1 Summary

The R and Swift workers no longer inherit Ubuntu Noble base findings. Swift runs on the
official Amazon Linux 2023 image with 0 vulnerabilities, and R 4.6.1 is compiled from the
checksummed upstream tarball on Debian 13. Publish run
[45708715797](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45708715797) promoted 31 version tags and 31 matching `latest` aliases on
Docker Hub, each a linux/amd64 plus linux/arm64 index. GitHub release [v2.1.1](https://github.com/sadatnfs/ds60sqlpy/releases/tag/v2.1.1)
targets `658d0cea826a63d3181ac198ead64c3c9b9dbaa9` and is Latest; it supersedes 2.1.0.

## Approach

1. **Swift on Amazon Linux 2023.** `docker/workers/Dockerfile.swift` starts from the pinned
   `swift:6.3.3-amazonlinux2023` digest, applies `dnf upgrade --releasever=latest` and runs the
   worker on python3.12. The Swift answers whose output depends on the platform were refreshed.
2. **R from source on Debian 13.** `docker/workers/Dockerfile.r` has four stages: cairo 1.18.6
   from source without X11, R 4.6.1 from the checksummed tarball, builder-only headers, and a
   runtime that keeps the C, C++ and Fortran toolchain. The local image is 1.25 GB, down from
   1.87 GB on Noble. tmb-local and Spark/TMB were rebuilt on it.
3. **Scans and policy.** The pinned Trivy found no fixable findings in the R, tmb-local and
   Spark/TMB images; their 87 HIGH or CRITICAL pairs are covered by the shared Debian 13 policy
   entries. `13b2ace2` removed 162 Noble `linux-libc-dev` entries, leaving 94 pending-owner
   entries (60 expire 2026-12-23, 34 expire 2026-12-24).
4. **Release.** `15e28332` bumped the release to 2.1.1. Runtime qualification passed for `r`
   and `swift` on native amd64 and arm64 runners, every workflow triggered by the release
   commit passed, and a Docker Hub manifest check resolved all 62 tags to two-platform
   indexes, with each alias digest equal to its version tag.

## Verification

- Runtime qualification: `r` on both architectures in 45685527345; `swift` on both
  architectures in 45679461808 and again after the python3 fix in 45697339763.
- Green on `658d0cea`: Course validation 45708715856, CodeQL 45708715883, Targeted classroom
  images 45708715666 and Application builds 45708715732 (portable starter; a publish commit
  leaves the Docker groups to the publish workflow). Application builds 45697229555 ran every
  Docker worker group, including all 96 Swift guide samples, on `2fa88aac`, whose only
  successor is the release commit.
- Publish 45708715797, attempt 2: all 44 jobs passed, including 40 Qualify jobs (20 groups on
  native amd64 and arm64), promotion, and both fresh-pull jobs that inspect every published
  index and run a native Core starter. The Standalone Spark PyTorch package check passed in
  45721660585.
- `scripts/image_scan.py validate-policy` passes with 94 entries.
- Full parallel test run on `c45a7170`: 6,268 passed, 520 skipped and 30 subtests passed,
  exit 0. Local Swift guide examples on the fixed image: 96 passed, 0 failed.
- Security alerts: 105 Dependabot alerts fixed and none dismissed, 2 CodeQL alerts fixed, and
  0 secret-scanning alerts.

## Deviations

- **r-059 figures.** R built without Pango defaulted bitmap devices to Xlib, so the r-059
  ggplotly example failed in runtime qualification. `954ab255` makes cairo the default in the
  runner and in Rprofile.site, and the image build smoke-tests `png()`.
- **History secret scan deadlock.** `git cat-file --batch` was fed and read through two pipes
  and hung for 41 minutes on the full history. `9d8ab4d4` writes the object IDs to a temporary
  file first.
- **Dockerfile.r format drift.** Course validation 45679882716 failed the format check;
  `c45a7170` applied the formatter.
- **Swift guide examples.** Application builds 45690405817 failed all 96 Swift guide examples
  with `TypeError: write_text() got an unexpected keyword argument 'newline'`, because the
  checker starts the driver with `python3`, the system 3.9 on Amazon Linux 2023. Runtime
  qualification did not catch it because it starts the worker through its python3.12
  entrypoint. `2fa88aac` links `/usr/local/bin/python3` to python3.12 while dnf keeps
  `/usr/bin/python3`.
- **Local App qualification.** Twelve `uv.lock` pins (for example `certifi==2026.11.20`) were
  not yet on the Microsoft package feed, so App qualification ran on GitHub runners instead of
  locally.
- **Promotion gate.** Publish attempt 1 qualified all 20 groups, but promotion stopped at the
  exact-revision gate after its 15-minute wait, because the dispatch-only
  `verify-torch-package.yml` had not run for `658d0cea`. Dispatching it (45721660585) and
  rerunning only the failed jobs promoted the qualified images without a rebuild, as the
  runbook in `docs/dockerhub.md` describes. No tag reached Hub before promotion. Future
  releases should dispatch that check right after pushing a `[publish-docker]` commit.
- **Release-notes evidence link.** The notes draft cited runtime qualification 45679461808,
  which failed overall on `15e28332` (`r`, before the cairo fix). The published notes cite
  45685527345 for `r` and 45697339763 for `swift`.
- **Abandoned agent PR.** A Copilot coding-agent draft (PR 26) was opened against the attempt-1
  promotion failure. It had no file changes, so it was closed with an explanation.

## Self-Check: PASSED

Tasks 1 to 4 map to 15e28332, 13b2ace2, 954ab255, 9d8ab4d4, c45a7170 and 2fa88aac, with the
release commit 658d0cea and the evidence commit a2285ec3. Release v2.1.1 is published
with 31 version tags and 31 `latest` aliases, all verified multi-arch, and HARD-01, HARD-04 and HARD-05 are complete.
