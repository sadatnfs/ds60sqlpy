---
phase: 01-qualify-1-4-4-guide-python-sql-walkthroughs
plan: 05
type: verification
status: human_needed
---

# Phase 1 verification: guide, tour and Python/SQL walkthroughs

This file records what was checked for the end-of-phase review and how.
It never includes the classroom URL, secrets or the text of any learner draft.

## Manual review outcomes

Manual clarity outcome: UNAVAILABLE - autopilot run with no first-time reviewer present. The automated browser check confirmed that the manual opens from both home and the workspace, explains every control and returns to the same lesson. Human clarity still needs a first-time reviewer.
Tour selection and draft preservation: PASS - in a real Chromium run, all 10 tour and solution inspections kept the same selected lesson and the same draft SHA-256 (table below).
Observed confusion: UNAVAILABLE - with no human reviewer, there were no observations. The automated run found no stuck states, uncaught exceptions, failed HTTP requests or external requests.

## Review conditions

| Field | Value |
|-------|-------|
| Reviewer first-time status | Unavailable: no first-time human reviewer in this autopilot run. Evidence comes from the automated checker only. |
| Desktop viewport | 1440 x 1000 CSS pixels, Chromium 156.0.8078.4 (`scripts/check_classroom_browser.py`) |
| Disposable target | Confirmed: a dedicated classroom project prepared with `--starter` and checked with `--confirm-disposable`. The URL is not recorded. The learner's own classroom project and volumes were not touched. |
| Checker result | `checker_exit=0`, report `"complete": true`, 20 of 20 checks passed |
| Full pytest suite | 5694 passed, 520 skipped, 0 failed |
| Docker Hub instruction | Not run, edited or endorsed. Only source-verified local guidance was assessed. |

## Solution preservation outcomes

| Solution | Outcome |
|----------|---------|
| Python worked solution (`python-02`) | PASS: walkthrough request is distinct from Run. Learner source, notes, selection, progress, receipts and history are unchanged. |
| SQL Exercise 1 solution (`sql-start-02`) | PASS: walkthrough request is distinct from Run. Learner source, notes, selection, progress, receipts and history are unchanged. |

## Per-inspection lesson and draft digests

Each draft digest is the SHA-256 of the saved editor draft, taken before and after the inspection. Draft contents are not recorded.

| Inspection | Lesson before | Lesson after | Draft SHA-256 before | Draft SHA-256 after | Result |
|------------|---------------|--------------|----------------------|---------------------|--------|
| Declining the tour offer | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| The Python practice walkthrough | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| The Python solution walkthrough | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| Starting the tour from the manual | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| Ending the tour | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| Dismissing the restarted tour | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| Completing the tour | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| Returning from home to start the tour | python-02 | python-02 | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | `1fe3a86581c42146e9a80e1cf751bc3bc3ad13bc0b155676e35de35309fcc654` | PASS |
| The SQL practice walkthrough | sql-start-02 | sql-start-02 | `6441db3478dc33d3f3daa4aeb6378dbeb3c89aaf7daf346ee7625104ea2307d6` | `6441db3478dc33d3f3daa4aeb6378dbeb3c89aaf7daf346ee7625104ea2307d6` | PASS |
| The SQL solution walkthrough | sql-start-02 | sql-start-02 | `6441db3478dc33d3f3daa4aeb6378dbeb3c89aaf7daf346ee7625104ea2307d6` | `6441db3478dc33d3f3daa4aeb6378dbeb3c89aaf7daf346ee7625104ea2307d6` | PASS |

The deliberate lesson switch made before the SQL inspections sets a new baseline. It is not counted as a preservation failure.

## SQL solution walk probe history

A probe stepped through every fenced block in every SQL Markdown solution, using its trusted setup context, on the disposable PostgreSQL 17 classroom.

| Run | Step errors | Change behind the improvement |
|-----|-------------|-------------------------------|
| Baseline | 160 | none |
| Context slicing | 9 | Exercise-marker and numbered-section context, solution prefix replay |
| Includes and `\gset` | 4 | `\ir` inlining and send-buffer meta-commands |
| Content and friendly message | 1 | sql-52 Exercise 2 Markdown fix; read-only message |

Final probe: 509 ok, 68 expected unsupported, 1 step error.
The remaining error is `sql-sec-01` #9, an INSERT through a SECURITY DEFINER function. Step-through is read-only by design, so this block now shows the friendly message "This step calls something that changes data, and step-through runs read-only, so use Run to see it work." Run still works for this block.

## Checker list (20 of 20 passed)

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
17. js-029 completed reference passes real browser interaction checks
18. js-030 completed reference passes real browser interaction checks
19. js-031 completed reference passes real browser interaction checks
20. No uncaught JavaScript exceptions, HTTP failures or external requests

## Open item

Human first-time clarity is still UNAVAILABLE. To close it, have a reviewer who has never seen the classroom follow the human-check scenario in `01-05-PLAN.md` on a disposable desktop classroom, then replace the two UNAVAILABLE lines above.
