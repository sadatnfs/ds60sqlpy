---
phase: 09-code-desktop-acceptance-gates
type: verification
status: in_progress
---

# Phase 9 verification: repository and desktop acceptance gates

This file records the acceptance evidence for the overhaul. It never includes a
classroom URL, secrets or the text of any learner draft.

## 09-01 repository acceptance gate (QUAL-01)

Status: pending. This gate must run on the exact release candidate commit, so
it is recorded with the 2.0.0 release in Phase 10.

Pre-flight on `2f9521b2` (`work/p9/gates.sh`) found three failures, all fixed
in the working tree before the release commit:

| Gate | Finding | Fix |
|------|---------|-----|
| `scripts/normalize_lesson_prose.py` | Java `java-009` regenerated with code spans that the `closeA` prose rule rewrites; `llm-applied-019` math | Java authoring specs now emit code spans (`courses/java/authoring/specs.py`), Java regenerated and formatted; math normalized to `\(\log(2)\)` |
| Dash scan | One en dash added in `.github/copilot-instructions.md` | Replaced with "to" |
| `./scripts/lint-repo` | ShellCheck SC2034 on `database_from_hub` in `scripts/classroom_images.sh` | Scoped `shellcheck disable=SC2034` directive |

## 09-02 desktop browser acceptance (QUAL-02)

Result: PASS.

| Field | Value |
|-------|-------|
| Workflow | `Browser acceptance` (`.github/workflows/browser-acceptance.yml`), run 45368870932, conclusion `success` |
| Commit | `2f9521b20dcd57938193d34036de2783ee619048` |
| Window | 2026-11-24T09:49:39Z to 2026-11-24T10:07:04Z |
| Browser | Chromium 156.0.8078.4, headless, 1440 x 1000 CSS pixels |
| Stack | Disposable starter classroom built from the commit through `./classroom`, project `ds60-ci-browser-acceptance` on a hosted runner (never `ds60-classroom*`) |
| Receipts | `"complete": true` for the main, restart-write and restart-verify receipts; runtime-failure receipt `passed: true` for every case |
| Teardown | Step "Remove the disposable classroom and its volumes" succeeded: `down --volumes --remove-orphans` on the disposable project only |

Deviation from the plan: the plan named a local project `ds60-phase9-browser`.
The gate ran on a hosted runner instead, so the local Docker host, learner
volumes and protected containers were never involved. The stack was built from
the same commit through the same `./classroom` launcher.

### Checks (27 of 27 passed)

1. All 40 subjects are selectable; home fits desktop and narrow viewports
2. Day 02 setup steps retain 1, 2, 3, 4 across commands and paragraphs
3. Declining the optional tour preserves the lesson and learner state
4. Python practice step-through traces the saved draft without a Run
5. Python solution step-through uses a distinct request and preserves learner state
6. The manual explains its controls and returns to the same lesson
7. The lesson tour starts, dismisses, restarts and completes without data loss
8. Starting a tour from home returns to the previously selected lesson
9. Fresh Python execution and receipts; readable output and prose in both appearances
10. SQL practice step-through shows FROM, WHERE, SELECT and ORDER BY rows
11. SQL Exercise 1 solution step-through preserves the learner draft
12. Python, SQL and module source, notes and results remain isolated across switching
13. Textbook renders MathML and syntax colors; chapter fits a narrow viewport
14. No-selection home and manual tour entries stay put and request no execution
15. A fresh browser restores server-saved progress, notes, pads and run results
16. Saved Plotly SVGs fit desktop, mobile and reopened panels; original JSON stays exact
17. Workspace strip, Run label and Result panel match 8 lesson modes
18. The go-001 authored walkthrough opens, steps and closes without a run
19. A keyboard-only learner can skip, search, save, run, jump to results and review
20. 159 keyboard focus stops show a visible cue
21. A stale browser copy is offered, kept and discarded without replacing the draft
22. Drafts survive reload and lesson switches; SQL reset and history never run or save
23. js-029 completed reference passes real browser interaction checks
24. js-030 completed reference passes real browser interaction checks
25. js-031 completed reference passes real browser interaction checks
26. axe-core 4.14.1: no serious or critical findings on 16 scans
27. No uncaught JavaScript exceptions, HTTP failures or external requests

The product scope is desktop only. Checks 1, 13 and 16 and the
`*-mobile.png` screenshot names come from the checker's earlier wording; the
narrow-viewport assertions are extra layout coverage, not a mobile support
claim.

### Plan coverage

| Plan item | Evidence |
|-----------|----------|
| Operating manual and links | Checks 6 and 14 |
| Lesson switching (palette and list) | Checks 1, 12 and 19 |
| Workspace mode strip | Check 17: 8 lesson modes sampled: legacy Python, SQL snippet, SQL lesson, module ready, module not ready, module reading, offline DAX and browser preview |
| Python and SQL walkthroughs (open, step, leave) | Checks 4, 5, 10 and 11 |
| Non-Python/SQL walkthrough | Check 18: `go-001`, 5 steps, first step "Package and imports", keyboard stepping, only a `walkthrough` request, no run |
| Run, save, history, SQL practice reset | Checks 9, 19 and 22 |
| Keyboard-only flow | Check 19: skip to content, palette opens a lesson and is ignored inside the editor, save and run shortcuts, leave editor, skip to result, open an old run, tour traps focus |
| Focus cues | Check 20: lessons `bridge-01` and `apache-004`, 159 stops, 0 failures, one allowlisted stop (`.cm-content` via `.code-editor:focus-within`) |
| axe in both themes | Check 26: tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa; home, legacy Python, SQL snippet, module reading, offline DAX, module not ready, browser preview and the palette, each in light and dark; 0 blocking, 0 recorded |
| Draft preservation across reload and restart | Checks 15, 21 and 22, 20 preservation inspections, and the restart-write and restart-verify receipts (`bridge-01` draft intact after the lab container restart) |
| Python run that raises | Runtime-failure case `syntax` (`llm-011`, python-core): job `failed`, return code 1, execution verified, source and notes restored |
| Stopped worker reported and recovered | Runtime-failure case `timeout-and-recovery`: the worker job is killed (`timed_out`, return code -15), then a recovery job `succeeded` with return code 0 and recovery verified. A worker that is down entirely is covered by unit tests: `tests/test_module_worker.py:185` and `tests/test_module_jobs.py:240`, plus the browser's "module not ready" mode sample |
| Invalid SQL statement | Not a browser case. Covered by the run-explain fixtures in `tests/fixtures/run_explain/sql.json` (division by zero, an unknown column and a `SELEC` syntax error) and by the error-navigation case for a PostgreSQL syntax error at `tests/test_learning_editor.py:52` |
| Stale walkthrough hidden, not shown | Check 18 `stale_hidden: "server-validated"`: the server validates the walkthrough reference before it is offered |
| Teardown, protected stacks untouched | Teardown step success; hosted runner, so no local learner volume existed to touch |

### Receipt digests (SHA-256)

| Receipt | SHA-256 |
|---------|---------|
| `browser-receipts.json` | `960fef1819863715d14bd14ee95b37726652280c831ea247adca9e7caf70a570` |
| `restart-marker.json` | `b1f160b9e9c242b6b080926d03d2ab138c09980e5fcc78f6d0a1e48dc3e60a8e` |
| `restart-write.json` | `daa1f3dcedfa8437564bf4ba75b7a710e0ccc9eed3879a5db4bdb29dfce855a9` |
| `restart-verify.json` | `4ade452d6f079730ad8d4e7c9b91dda859a68605cb2da6edbf860ae096099302` |
| `runtime-failures.json` | `49ab71cf0b1fd956c2f06d63805d990dec2beac19144dafd947ef6b641e0b20b` |

The receipts come from the run's `browser-acceptance-receipts` artifact.

### Human review

Not available in this autopilot run. A first-time desktop reviewer should
still confirm clarity of the manual, tour and walkthroughs before the release
is announced.
