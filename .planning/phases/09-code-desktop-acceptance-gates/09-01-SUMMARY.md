---
phase: 09-code-desktop-acceptance-gates
plan: 01
subsystem: repository-acceptance
status: complete
requirements: [QUAL-01]
tags: [gate, pytest, ruff, mypy, lint, format, content-checks]
requires: [07-04, 08-04, 08.1-01]
provides:
  - .planning/phases/09-code-desktop-acceptance-gates/09-VERIFICATION.md (QUAL-01 section)
affects: [10-01]
key-files:
  created:
    - .planning/phases/09-code-desktop-acceptance-gates/09-01-SUMMARY.md
  modified:
    - .planning/phases/09-code-desktop-acceptance-gates/09-VERIFICATION.md
    - courses/java/authoring/specs.py
    - .github/copilot-instructions.md
    - scripts/classroom_images.sh
decisions:
  - The gate ran on the release candidate working trees (bca223a5 and 7c322a8d) and the hosted Course validation on the tagged commit a4354ff8 is the gate of record for the release.
  - The scratch gate runner lives under work/ (not tracked); each gate's exit status and summary line is copied into 09-VERIFICATION.md.
commits: 0
actuals:
  tasks: 3
  commits: 0
completed: 2026-11-24
---

# Phase 9 Plan 01: repository acceptance gate Summary

Every repository check that covers the overhaul passes on the release line (QUAL-01 PASS).

- Local gates: 13 of 13 rc=0 at `bca223a5` and again at `7c322a8d`
- Hosted gate of record: Course validation
  [45460757714](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45460757714) on `a4354ff8`
  (tag `v2.0.0`), conclusion `success`
- Closeout full pytest: 5838 passed, 514 skipped; the one `-n auto` failure (Apache
  `ballista` resume timeout) passed serially

## What was done

- Pre-flight on `2f9521b2` found three failures (lesson prose normalization for Java and one
  math span, one en dash, one ShellCheck SC2034). All three were fixed in the tree before the
  release commit; the fixes are listed in `09-VERIFICATION.md`.
- The 13 gates (ruff check and format, mypy, module, walkthrough, track qualification,
  coverage matrix, prose normalization, classroom UI, public release scan, dash scan,
  `lint-repo`, `format-repo`) then passed twice on the release line.

## Deviations

- The commits for the fixes landed in the release commit `ca8ef9a3` and its follow-ups rather
  than in separate Phase 9 commits, so this plan records 0 commits of its own.
- The full-suite total recorded earlier (6196 passed, 520 skipped) could not be reproduced at
  closeout; `09-VERIFICATION.md` now records the closeout run as the figure of record.

## Self-Check: PASSED
