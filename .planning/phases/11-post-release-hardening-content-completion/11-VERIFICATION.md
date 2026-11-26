---
phase: 11-post-release-hardening-content-completion
type: verification
status: passed
verified: 2026-11-25
score: 7/7 success criteria
covered_files:
  - .planning/phases/11-post-release-hardening-content-completion/11-01-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-01-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-02-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-02-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-03-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-03-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-04-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-04-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-05-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-05-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-06-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-06-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-07-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-07-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-08-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-08-SUMMARY.md
  - .planning/phases/11-post-release-hardening-content-completion/11-09-PLAN.md
  - .planning/phases/11-post-release-hardening-content-completion/11-09-SUMMARY.md
  - .github/workflows/codeql.yml
  - docker/cve-policy.json
  - docker/workers/Dockerfile.r
  - docker/workers/Dockerfile.swift
  - scripts/check_guide_examples.py
  - scripts/check_no_dashes.py
  - scripts/check_r_toolchain.py
covered_digest: v4:sha256:d054590f3b702fbec09de8138626125933b393008a1222b59f97662295881f61
---

# Phase 11 verification: post-release hardening and content completion

Requirements: HARD-01 to HARD-07. Plans 11-01 to 11-09 all have SUMMARYs. Release
[v2.1.1](https://github.com/sadatnfs/ds60sqlpy/releases/tag/v2.1.1) (Latest, targeting
`658d0cea826a63d3181ac198ead64c3c9b9dbaa9`) carries every change; 2.1.0 and 2.0.0 stay listed below it.

## Success criteria

| # | Criterion | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | Fixable image and repository findings are fixed: no shipped Dockerfile misconfigurations in the app image, fewer kernel-header and base-image findings, CodeQL on every push, current justifications for the rest (HARD-01) | PASS | 11-04 removed the repository Dockerfiles from the App image (27 DS-0002 entries to 0), added CodeQL on every push and pull request plus weekly, and relocked Python, Node and Go to every patched version. 11-09 moved Swift to Amazon Linux 2023 (0 vulnerabilities) and rebuilt R from source on Debian 13; tmb-local and Spark/TMB have no fixable findings. The policy fell from 276 entries to 94, all `pending-owner` with expiry dates of 2026-12-23 or 2026-12-24, and `validate-policy` passes. GitHub shows 105 Dependabot alerts fixed and none dismissed, 2 CodeQL alerts fixed, and 0 secret-scanning alerts. CodeQL [45708715883](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45708715883) passed on the release commit. |
| 2 | Lessons teach lesson-specific material: templated prose down by at least half, no lesson above 50% templated words, shared instructions in one linked guide (HARD-02) | PASS | 11-07 cut templated prose words from 835,161 to 71,137 (91.5 percent). The largest per-lesson share is 0.32 (`mle-011`); `test_no_lesson_is_mostly_templated_prose` enforces 0.50 and `docs/coverage-matrix.md` prints both numbers. Each of the 21 rewritten tracks links one `STUDY-GUIDE.md`. |
| 3 | Every runnable guide sample runs in its own runtime through an automated harness; failures are fixed or marked as fragments (HARD-03) | PASS | `scripts/check_guide_examples.py` (11-06) runs or statically checks every fenced block, with `fragment`, `external`, `expect-error`, `isolated`, `prelude=` and `profile=` annotations. CI runs it for host, PostgreSQL and advanced Python in Course validation and for every Docker worker group in Application builds. Application builds [45697229555](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45697229555) passed every Docker worker group on `2fa88aac`, including all 96 Swift samples; the release commit `658d0cea` is its only successor and adds only the planning record `11-08-SUMMARY.md` (the 2.1.1 version bump landed earlier in `15e28332`). |
| 4 | The R worker keeps a C, C++ and Fortran toolchain, and a test builds and loads a compiled source package (HARD-04) | PASS | 11-03 kept gcc, g++, gfortran, make and the C library headers and added `scripts/check_r_toolchain.py`, which builds C, C++ (cpp11), Fortran and Rcpp packages offline in the `r` CI group; `tests/test_r_toolchain.py` blocks the purge from returning. The 11-09 Debian 13 runtime keeps the toolchain, and runtime qualification 45685527345 passed `r` on amd64 and arm64. |
| 5 | Scientific-project images are pushed only from GitHub Actions, scan-gated, as multi-architecture manifests (HARD-05) | PASS | 11-05 added scan-gated staging and promotion for the project images. Publish [45708715797](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45708715797) promoted `2.1.1-project-*` and the `latest-project-*` aliases, and `hub_manifests.py` resolved each to a linux/amd64 plus linux/arm64 index. No image was pushed from the local machine. |
| 6 | The full suite passes repeatedly under parallel execution with no known flaky tests (HARD-06) | PASS | 11-02 made the hang guards load-tolerant and the slow-subscriber test deterministic. Full `-n auto` runs: two consecutive on `eef105f2` and one on `c45a7170`, each 6,268 passed, 520 skipped and 30 subtests passed, exit 0. |
| 7 | No tracked first-party file has an em or en dash, and a repository-wide gate enforces it (HARD-07) | PASS | `scripts/check_no_dashes.py` (11-01) runs in Course validation on every push. Local run at closeout: "No em or en dashes in 17619 tracked files (vendored bundles exempt)." |

## Deviations recorded

- **Two release numbers.** Images changed after 2.0.0, so Phase 11 shipped as 2.1.0 (publish
  45653905041) and then 2.1.1 (publish 45708715797) once R and Swift moved off Ubuntu Noble.
  Published tags were never overwritten.
- **Failed publish attempts stopped before promotion.** 2.1.0 needed four publish runs
  (Maven 429s, new upstream kernel-header CVEs and fixable project-image CVEs). No partial tags
  reached Hub. See `11-08-SUMMARY.md`. The first 2.1.1 attempt also stopped before
  promotion: the exact-revision gate waited for the dispatch-only PyTorch package check, which
  had not run. After dispatching it (45721660585), rerunning only the failed jobs promoted the
  qualified images without a rebuild. See `11-09-SUMMARY.md`.
- **Fixes found during 2.1.1 qualification.** The r-059 cairo default (`954ab255`), the history
  secret-scan deadlock (`9d8ab4d4`), Dockerfile.r format drift (`c45a7170`) and the Swift
  `python3` link for the guide harness (`2fa88aac`). See `11-09-SUMMARY.md`.
- **Local App qualification moved to Actions.** Twelve `uv.lock` pins were not yet on the
  Microsoft package feed, so App images were qualified on GitHub runners.

## Kept for the owner to decide

- 94 `pending-owner` CVE policy entries (unfixable upstream base packages); 60 expire on
  2026-12-23 and 34 on 2026-12-24, when the policy gate will require a fresh review.
- The Phase 1 and Phase 6 human UAT items and the R11 human clarity review.
- Maven Central 429 responses that occasionally fail a Qualify job and need a failed-job rerun.
- The BuildKit cache (about 60 GB) and `~/.cache/ds60sqlpy`.
- Microsoft package feed lag for new `uv.lock` pins on local App builds.
