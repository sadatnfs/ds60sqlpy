---
phase: 11-post-release-hardening-content-completion
plan: 01
subsystem: content-gates
status: complete
requirements: [HARD-07]
requirements-completed: [HARD-07]
tags: [content, punctuation, gate, ci, generated-pages]
requires: []
provides:
  - scripts/check_no_dashes.py, a repository-wide em and en dash gate over git ls-files
  - a core CI step that fails on any new em or en dash in tracked text
  - tracked first-party text with no U+2014 or U+2013 outside vendored bundles
affects: [11-06, 11-07]
key-files:
  created:
    - scripts/check_no_dashes.py
    - tests/test_check_no_dashes.py
    - .planning/phases/11-post-release-hardening-content-completion/11-01-SUMMARY.md
  modified:
    - .github/workflows/ci.yml
    - AGENTS.md
    - CONTRIBUTING.md
    - docs/walkthroughs.md
    - scripts/build_course_guide.py
    - scripts/normalize_notebooks.py
    - scripts/image_scan.py
    - src/ds60sqlpy/sql_notebook.py
    - tests/test_course_guide.py
    - tests/fixtures/run_explain/swift-linux.json
    - START_HERE.html
    - curriculum/coverage-matrix.json
decisions:
  - Vendored third-party files stay untouched and are allowlisted by pattern (src/ds60sqlpy/assets/vendor/*.min.js, *LICENSE*, textbook/katex*.js, textbook/*LICENSE*) rather than by a list of single paths.
  - The gate reads git ls-files and skips binaries (a NUL byte in the first 8192 bytes, or invalid UTF-8), so untracked scratch under work/ never affects it.
  - Ranges became "to" or a hyphen (for example "Days 15-16"); clause dashes became commas, colons, parentheses or new sentences. No mechanical " - " substitution.
  - Tests that must name the characters use "\u2014" and "\u2013" escapes.
commits: [87af270e]
actuals:
  tasks: 4
  commits: 1
completed: 2026-11-24
---

# Phase 11 Plan 01: remove every em and en dash and gate the repository Summary

Tracked first-party text no longer contains an em dash (U+2014) or en dash (U+2013), and the
core CI job runs `scripts/check_no_dashes.py` so a new one fails the build (HARD-07). One commit,
87af270e, changed 187 files (2 added, 185 modified; 1158 insertions, 981 deletions) and removed
913 dash characters (371 em, 542 en) without adding any.

## Gate

- `scripts/check_no_dashes.py` (109 lines) reads `git ls-files -z`, skips binaries and the vendored
  allowlist, and prints each finding as `path:line:col: em dash` or `en dash`. It accepts optional
  path arguments and `--root`, and exits nonzero on any finding.
- `.github/workflows/ci.yml` core job: new step "Reject em and en dashes in tracked text" running
  `uv run --no-sync python scripts/check_no_dashes.py`, placed directly after "Check public
  release content boundaries" as the plan asked.
- `tests/test_check_no_dashes.py` has 3 tests:
  `test_reports_each_dash_with_position_and_skips_vendor_and_binary`, `test_clean_tree_passes`
  and `test_repository_has_no_dashes_outside_vendored_bundles` (the last runs the gate against
  the real checkout).
- `AGENTS.md` points authors at the gate and `CONTRIBUTING.md` adds the command to the local
  check list.

## Rewrite

Files changed by area (from `git show --stat`):

| Area | Files |
| --- | --- |
| `lesson-pages/` (generated) | 39 |
| `sql/postgres-60day/companion-guides/` | 23 |
| `courses/statistics-ml/chapters/` | 18 |
| `reference-pages/courses/statistics-ml/chapters/` (generated) | 18 |
| `python/professional/lessons/` | 10 |
| `sql/postgres-60day/solutions/` | 9 |
| `docs/` and `reference-pages/docs/` | 8 and 8 |
| `tests/` | 7 |

The rest are `START_HERE.html`, `curriculum/coverage-matrix.json`,
`courses/statistics-ml/coverage.json`, `source-outline.md`, bridge guides and a few scripts.

- Sources were rewritten in context. `scripts/build_course_guide.py` and
  `tests/test_course_guide.py` now emit and expect hyphenated day ranges such as "Days 15-16".
- `tests/test_dbt_course.py`, `tests/test_polars_course.py`, `tests/test_ml_engineering_course.py`
  and `tests/test_practice_audit.py` use `"\u2014"` escapes where they assert the character is
  absent.
- `tests/fixtures/run_explain/swift-linux.json`: the en dashes in recorded Swift backtrace
  address ranges became hyphens.
- `scripts/normalize_notebooks.py` and `src/ds60sqlpy/sql_notebook.py` no longer emit the
  characters.
- Derived output (lesson pages, reference pages, `START_HERE.html`, coverage matrix) was
  regenerated in the same commit, so generated pages match their sources.

## Verification

- Gate behavior on dashes, vendor files, binaries and a clean tree: covered by
  `tests/test_check_no_dashes.py`.
- Repository is clean outside the allowlist: covered by
  `test_repository_has_no_dashes_outside_vendored_bundles` and by the new CI step on every push.
- Generator drift: the regenerated pages are committed with their sources, and the existing
  generated-output drift checks in CI cover them.
- Day-range wording: covered by `tests/test_course_guide.py`.

## Deviations

- **Unrelated 11-05 work rode in this commit.** `scripts/image_scan.py` gained
  `SCIENTIFIC_PROFILES` (`project-spark-torch` maps to `spark-local-python` and `llm-torch-cpu`;
  `project-spark-tmb` maps to `spark-local-python`, `r-statistics` and `java21`), so base-image
  CVE policy entries also cover the scientific project images. It belongs to plan 11-05 and is
  recorded there.
- The vendored allowlist uses patterns rather than the single `textbook/katex.js` path the plan
  named, so every third-party bundle and license file is covered.

## Self-Check: PASSED
