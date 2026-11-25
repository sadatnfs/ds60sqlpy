---
phase: 11-post-release-hardening-content-completion
plan: 03
subsystem: r-worker
status: complete
requirements: [HARD-04]
requirements-completed: [HARD-04]
tags: [docker, r, toolchain, compiled-packages, qualification, ci]
requires: []
provides:
  - an R statistics worker that keeps gcc, g++, gfortran, make and the C library headers
  - scripts/check_r_toolchain.py, a classroom-job probe that builds C, C++ (cpp11), Fortran and Rcpp code offline
  - a static test that the toolchain purge cannot return
affects: [11-04, 11-08]
key-files:
  created:
    - scripts/check_r_toolchain.py
    - tests/test_r_toolchain.py
    - .planning/phases/11-post-release-hardening-content-completion/11-03-SUMMARY.md
  modified:
    - docker/workers/Dockerfile.r
    - scripts/ci_classroom.py
    - tests/test_ci_classroom.py
    - courses/r/README.md
    - courses/r/authoring/build.py
    - docker/workers/r/README.md
    - docker/cve-policy.json
decisions:
  - The probe runs as an ordinary classroom job (lesson r-001, purpose "solution") so it exercises the same no-network, read-only, non-root runner learners use, not a privileged docker exec.
  - The probe builds into a per-job library with R CMD INSTALL, so nothing is written to the image library.
  - The probe covers C++ through both cpp11 and Rcpp as well as C and Fortran, because learner packages commonly use either C++ interface.
  - The linux-libc-dev kernel header findings the kept headers bring are handled only as pending-owner policy entries with the existing justification. None was approved on the owner's behalf.
commits: [e9892d22, 930d28de]
actuals:
  tasks: 3
  commits: 2
completed: 2026-11-24
---

# Phase 11 Plan 03: let the R worker build packages from source Summary

The R statistics worker keeps its compilers, so learners can install source packages with C,
C++ or Fortran code. CI qualifies this with a package-build probe in the `r` classroom group
(HARD-04). The implementation landed in e9892d22 (10 files, 332 insertions, 11 deletions). The
policy accounting landed in 930d28de with plan 11-04. The CI run of the probe on the released
image is verified in plan 11-08.

## Image

`docker/workers/Dockerfile.r` no longer runs
`apt-get purge -y gcc g++ gfortran cpp make linux-libc-dev libc6-dev`, and its comment now says
the compilers stay installed for learner package builds. R's `Makeconf` is unchanged and keeps
pointing at the system compilers at their default paths. The probe's `R CMD INSTALL` builds
depend on that.

## Qualification probe

`scripts/check_r_toolchain.py` (205 lines) submits one classroom job in the `r-statistics`
profile (lesson `r-001`, purpose `solution`, 120 s timeout inside a 150 s budget). The job:

- asserts it runs as a non-root user and that the image library `.Library` is not writable;
- writes a tiny package with C (`init.c`), C++ through cpp11 (`dot.cpp`) and Fortran
  (`scale.f90`) sources;
- runs `R CMD INSTALL` into a per-job library, loads the package and checks each routine with
  `stopifnot(identical(...))`;
- compiles and calls an Rcpp function;
- prints `r-toolchain checks passed: C, C++ (cpp11), Fortran and Rcpp`.

The probe also writes a JSON receipt. `scripts/ci_classroom.py` runs it for the `r` group as a
qualification check whose receipt is `r-toolchain-receipt.json`, and adds the probe script to
that group's source inputs.

## Tests

- `tests/test_r_toolchain.py` (5 tests):
  - `test_r_worker_keeps_the_compilers_that_learner_packages_need` fails if
    `apt-get purge|remove|autoremove` returns to `Dockerfile.r`.
  - `test_probe_builds_every_compiled_language_into_a_per_job_library`
  - `test_probe_runs_as_a_worked_solution_and_reports_success`
  - `test_probe_rejects_failed_or_incomplete_builds`
  - `test_probe_cancels_a_job_that_outlives_its_budget`
- `tests/test_ci_classroom.py`: `test_r_group_qualifies_compiled_package_builds`.

## CVE policy (task 3, in 930d28de)

Keeping `linux-libc-dev` in the R image surfaces kernel UAPI header findings that the other
images already carried. `r-statistics` was added to the `images` list of the 137 existing
`linux-libc-dev` entries in `docker/cve-policy.json`. Each entry keeps its reviewer
`pending-owner` and its justification: headers only, no fixed Debian version, and containers run
on the host kernel. No new entry was created and none was approved.

## Docs

`courses/r/README.md`, `courses/r/authoring/build.py` and `docker/workers/r/README.md` now say
the compilers stay installed, so a script can build a small source package from a local
directory with `R CMD INSTALL` or compile Rcpp and cpp11 code offline (not from CRAN). Their
reference pages were regenerated.

## Verification

- The purge cannot return: covered by `tests/test_r_toolchain.py`.
- Probe success, failure, incomplete-build and budget handling: covered by
  `tests/test_r_toolchain.py`.
- The `r` CI group runs the probe: covered by `tests/test_ci_classroom.py`.
- An R worker build and qualification in CI with the package-build check (the plan's
  verification) is part of the 2.1.0 release run recorded in plan 11-08.

## Deviations

- The plan asked for C and Fortran. The probe also builds C++ through cpp11 and Rcpp.
- Task 3 landed in the 11-04 commit 930d28de, because both plans edit the same policy file.

## Self-Check: PASSED
