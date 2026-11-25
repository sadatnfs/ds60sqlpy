---
phase: 11-post-release-hardening-content-completion
plan: 08
subsystem: release
status: complete
requirements: [HARD-01, HARD-02, HARD-03, HARD-04, HARD-05, HARD-06, HARD-07]
requirements-completed: [HARD-02, HARD-03, HARD-04, HARD-05, HARD-06, HARD-07]
tags: [release, ci, docker-hub, cve-policy, github-release]
requires: [11-01, 11-02, 11-03, 11-04, 11-05, 11-06, 11-07]
provides:
  - DS60 2.1.0 published from GitHub Actions as 37 multi-arch Docker Hub tags
  - GitHub release v2.1.0, marked Latest, targeting 8894b940
  - the four scientific project images published from Actions after scan gates
  - a CVE policy with current, expiring pending-owner entries for every unfixable finding
affects: [11-09]
key-files:
  created:
    - .planning/phases/11-post-release-hardening-content-completion/11-08-SUMMARY.md
  modified:
    - "VERSION and the 2.1.0 bump set (104 files in 8527f9e7)"
    - docker/cve-policy.json
    - scripts/ci_classroom.py
    - scripts/check_classroom_browser.py
    - "tests/{test_image_scan,test_ci_classroom}.py"
    - "packages/spark-likelihood (Lightning 2.6.6, PyArrow 23.0.1, setuptools 84.2.1, wheel 0.48.0)"
    - "courses/advanced-spark-modeling/projects (matching lock and image pins)"
    - docker/ci-scientific-projects.json
    - "docker/workers/requirements-torch.txt and courses/go fixture manifests (dependency graph comments)"
    - "README.md and docs/dockerhub.md (2.1.0 evidence, committed with 15e28332)"
decisions:
  - The release number moved to 2.1.0 because images changed; published 2.0.0 tags stay immutable.
  - A publish that fails on a real finding gets a new commit and a fresh [publish-docker] run, because a rerun reads the same policy. Only transient failures such as a Maven 429 are rerun in place.
  - Unfixable kernel-header CVEs on the Ubuntu-based R and Swift images were recorded as pending-owner entries, never dismissed. Removing them became plan 11-09.
  - Project image CVEs were fixed by upgrading the locked packages, not by policy.
commits: [b48bce7d, eef105f2, 8527f9e7, 400742c9, 8894b940, e06c85ba, 7ebd9fa6]
actuals:
  tasks: 4
  commits: 7
completed: 2026-11-25
---

# Phase 11 Plan 08: CI, release 2.1.0 and closeout Summary

DS60 2.1.0 shipped every Phase 11 change. Publish run
[45653905041](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45653905041) passed all 44
jobs on attempt 2 and promoted 37 Docker Hub tags, each a linux/amd64 plus linux/arm64
manifest. GitHub release
[v2.1.0](https://github.com/sadatnfs/ds60sqlpy/releases/tag/v2.1.0) targets
`8894b940aeb22c3934e3e4c423656dfe65f7b7ce` and was Latest until 2.1.1. The 1.4.1 release was
retired earlier, and 2.0.0 stays listed below 2.1.0.

## Approach

1. **Gates and CI.** The local repository gate passed except the known `.env` false positive.
   `eef105f2` fixed the python-core browser check, which still looked for the guidance text
   that 11-07 moved into the shared study guide.
2. **Bump and publish.** `8527f9e7` bumped the release to 2.1.0 across 104 files. Three
   publish commits were needed before promotion (see Deviations).
3. **Hub verification.** `files/p11/hub_manifests.py` resolved all 37 tags (App and
   PostgreSQL with their `latest` aliases, 25 workers, and the four scientific project images
   with their `latest-project-*` aliases) to two-platform manifests.
4. **Release and evidence.** The GitHub release notes record the publisher run, the source
   SHA and the scan gate. The README and `docs/dockerhub.md` evidence paragraphs for 2.1.0
   landed with the 2.1.1 bump commit `15e28332`.

## Verification

- Green on `8894b940`: Application builds 45653904909, Course validation 45653904960, CodeQL
  45653904855, Targeted classroom qualification 45653904902 and the CUDA torch verification
  45653987075.
- Publish 45653905041 attempt 2: 44 of 44 jobs succeeded, including scientific project
  qualification on both architectures and the promotion and pull checks.
- Security alerts: 105 Dependabot alerts fixed and none dismissed, 2 CodeQL alerts fixed, and
  0 secret-scanning alerts.
- HARD-06: two consecutive full parallel test runs on `eef105f2`, each 6,268 passed,
  520 skipped and 30 subtests passed, exit 0.

## Deviations

- **Four publish attempts.** All failed runs stopped before promotion, so no partial tags
  exist.
  - 45616254402 on `8527f9e7`: Qualify java (amd64) hit a Maven Central 429, and the R and
    Swift qualification jobs were blocked by new unfixed Ubuntu `linux-libc-dev` CVEs from the
    2026-11-25 Trivy database.
  - 45630767375 on `400742c9`: the policy commit recorded 27 kernel-header CVEs as
    pending-owner, adjusted the scan CLI tests' frozen clock, and renamed the R toolchain
    report so the worker-checks artifact uploads it. The run then failed Qualify scientific
    projects on fixable CVEs in the project images.
  - 45653905041 on `8894b940`: the project locks moved to Lightning 2.6.6, PyArrow 23.0.1,
    setuptools 84.2.1 and wheel 0.48.0. Attempt 1 failed only on a Maven 429 in Qualify
    scala-spark (amd64); attempt 2 passed.
- **Kernel-header policy growth.** The policy grew to 256 pending-owner entries, 182 of them
  `linux-libc-dev`, because of new upstream data rather than a regression. Plan 11-09 was
  added to remove them by moving Swift to Amazon Linux 2023 and building R from source on
  Debian 13.
- **Dependency graph.** `e06c85ba` and `7ebd9fa6` added comment lines so GitHub's dependency
  graph records the patched CUDA torch pin and the Go fixture manifests.
- **Closeout moved.** The phase closeout and local Docker cleanup from task 3 and task 4 run
  after release 2.1.1 in plan 11-09, so the records describe the final state once.

## Self-Check: PASSED

Tasks 1 and 2 map to b48bce7d, eef105f2, 8527f9e7, 400742c9 and 8894b940, with e06c85ba and
7ebd9fa6 as follow-ups. Release v2.1.0 is published with 37 verified multi-arch tags.
HARD-01 stays open in this plan and closes with 11-09.
