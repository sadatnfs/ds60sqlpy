---
phase: 06-desktop-workspace-learner-state
plan: 03
subsystem: classroom-ui
status: complete
requirements: [UX-02]
tags: [keyboard, focus, accessibility, desktop]
requires: [06-01]
provides:
  - "paletteShortcut(event, mac) pure helper (classroom-shell.js, // BEGIN SHELL KEY HELPERS)"
  - "inertBackground(doc, keep) pure helper (classroom-guide.js, // BEGIN TOUR INERT HELPER) wired into startTour and endTour"
  - "#skip-result skip link with focus handling to #results-title or #capability"
  - "#run aria-describedby=capability; palette and manual-parts focus cues"
affects: [06-04]
tech-stack:
  added: []
  patterns: ["marked pure helper block evaluated alone in a Node vm by pytest"]
key-files:
  created:
    - tests/test_classroom_keyboard.py
  modified:
    - src/ds60sqlpy/assets/classroom-shell.js
    - src/ds60sqlpy/assets/classroom-guide.js
    - src/ds60sqlpy/assets/classroom.html
    - src/ds60sqlpy/assets/classroom.css
decisions:
  - "The helper parameter is named mac, not isMac, so the plan's grep for paletteShortcut(event, isMac) matches only the call site (count 1)."
  - "The tab focus toggle row documents Ctrl M (Shift Alt M on a Mac). This was checked against the vendored CodeMirror bundle, which has {key:\"Ctrl-m\",mac:\"Shift-Alt-m\"}. A test pins that string."
  - "The palette footer's Ctrl K kbd gets class palette-key, and the shell rewrites it to Cmd K on a Mac. The footer stays short instead of spelling out both forms."
  - "Restoring inert runs in endTour before layer.remove() and before focus returns to the opener, so the opener is focusable again."
metrics:
  completed: 2026-11-24
actuals:
  tasks: 3
  commits: 0
  note: "The orchestrator makes the commits under exec-rules. This executor made none."
---

# Phase 6 Plan 03: Desktop keyboard and focus fixes Summary

This plan fixes research gaps K1 to K5 and adds a desktop jump to the Result area:
- **Palette shortcut (K3).** It follows platform conventions (Cmd+K on macOS, Ctrl+K elsewhere) and never fires inside CodeMirror.
- **Tour (K1).** While the tour is open, the rest of the page is inert.
- **Run button (K4).** A disabled Run points to `#capability` through `aria-describedby`, so screen readers announce why it is disabled.
- **Focus cues (K2, K5).** The palette search field and the manual parts show a visible accent cue of at least 3:1.
- **Skip link.** A second skip link, "Skip to result", lands on the Result heading, or on the capability note when the lesson has no Result.
- **Manual.** The in-app keyboard table documents all of this.

## What was done

**Task 1 (tracer): palette shortcut**
- Added `// BEGIN SHELL KEY HELPERS` with a pure `paletteShortcut(event, mac)`. It returns true only when the key is `k`, Alt and Shift are up, the target is not inside `.cm-editor`, and the platform modifier is exactly right.
- Added one shared `isMac` constant. The palette button's existing ⌘K label code now uses it too.
- The capture keydown listener calls `paletteShortcut(event, isMac)`. The Ctrl/Cmd+Enter `lastRun` line and the `/` shortcut are unchanged.
- Tracer gate: `tests/test_classroom_keyboard.py` passed before I expanded the work.

**Task 2: inert tour, Run description, skip to result**
- Guide:
  - Added `// BEGIN TOUR INERT HELPER` with `inertBackground(doc, keep)`. It returns a restore function that touches only the elements it changed.
  - `startTour` calls it right after `document.body.append(layer)` and stores `restoreInert` on `tour`.
  - `endTour` calls `restoreInert?.()` before `layer.remove()`.
  - The Next, Back and End tour controls live inside the layer, so they stay reachable.
- HTML:
  - Added `<a id="skip-result" class="skip" href="#runtime-results">Skip to result</a>` after the existing skip link.
  - Added `aria-describedby="capability"` to `#run`. Its existing attributes are kept, and the tag is now split across lines for width.
  - Added `tabindex="-1"` on `#capability` and `#results-title`.
- Shell: a click handler on `#skip-result` calls preventDefault. It focuses `#results-title` when `#runtime-results` is shown, and `#capability` otherwise.

**Task 3: focus cues, contrast and manual**
- CSS:
  - New `.palette-search:focus-within { box-shadow: inset 0 -2px 0 var(--accent); }`.
  - `.manual-parts li:focus` gains `box-shadow: inset 3px 0 0 var(--accent);`. Its outline and tint are kept.
  - Only existing tokens are used. Token values are unchanged, and nothing in the flagged legacy range was touched.
- Manual keys table:
  - The intro now says "unless the row names its own Mac keys".
  - The palette row reads "Ctrl K (Cmd K on a Mac) or /" and adds "except inside the code editor".
  - New row: "Ctrl M (Shift Alt M on a Mac)" switches whether Tab indents or leaves the editor.
  - New row: "Skip to result".
- The prose under "Search" now says "anywhere outside the code editor".
- The palette footer's Ctrl K is rewritten to Cmd K on a Mac.
- Tests (14 in total):
  - 15 shortcut cases checked in one vm call.
  - The keydown wiring.
  - The inert apply and restore vm case, plus the endTour ordering.
  - Static HTML checks using `html.parser`.
  - The skip handler.
  - The CSS rules.
  - Accent contrast against `--surface` and `--tint` in the light and dark token blocks, using `scripts.check_classroom_browser.contrast_ratio`.
  - The manual table text and the vendored CodeMirror binding.
  - A dash scan of the four assets.

05-02's walkthrough panel strings and 06-01's `dl#workspace-mode` are untouched. Each walkthrough string count is 2 in both classroom.html and classroom-guide.js, and `id="workspace-mode"` count is 1.

## Verification (real output, 2026-11-24)

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-06-03 -q tests/test_classroom_keyboard.py` | 14 passed |
| same plus `tests/test_web_development.py tests/test_module_ui.py` (plan verify) | 1 failed, 51 passed. The failure is `test_module_ui.py::test_async_classroom_ui_behaviors`: the pin expects 105 checks but the harness now reports 110 (06-02 in flight, see below). |
| `node scripts/check_classroom_ui.mjs \| tail -1` | `{"checks":110,"passed":true,"final":true}` |
| `.venv/bin/ruff check tests/test_classroom_keyboard.py` | All checks passed! |
| `.venv/bin/ruff format --check tests/test_classroom_keyboard.py` | 1 file already formatted |
| `.venv/bin/mypy src` | Success: no issues found in 62 source files |
| `node --check` on classroom-shell.js and classroom-guide.js | ok |
| dash scan (perl) on the 4 assets and the test file | no matches |
| grep acceptance counts | SHELL KEY HELPERS 1, `paletteShortcut(event, isMac)` 1, `inertBackground(document` 1, `id="skip-result"` 1, `aria-describedby="capability"` 1, `palette-search:focus-within` 1, `Cmd K` 2 |

How the harness and pin results developed:
- During the first run, the harness failed at check_classroom_ui.mjs:1312 ("old module browser drafts recover...", expected "old retained source").
- I copied the assets and harness to work/06-03/tree, removed my guide.js edits from the copy, and the same failure reproduced. So it was not caused by this plan.
- Minutes later, with 06-02's files updated, the harness passed in both the scratch copy (105 at that moment) and the real tree (110 on the final run).
- The 105 pin in test_module_ui.py belongs to 06-02, which still needs to update it to its final count.

## Deviations from Plan

1. **[Rule 1] The helper parameter was renamed to `mac`.** With `isMac` as the parameter name, the definition also matched the plan's grep, so the count was 2 instead of the required 1. Behavior is identical.
2. **[Rule 2] Two small additions so the docs match the behavior.**
   - The manual table intro says Mac users use Cmd "unless the row names its own Mac keys", because the Ctrl M row is not Cmd M on a Mac.
   - The palette footer's Ctrl K kbd (`.palette-key`) is relabeled Cmd K on a Mac by the shell.
3. **Plan assumption corrected.** The plan says the node harness does not load classroom-guide.js. It does (check_classroom_ui.mjs:8-9), and it loads classroom.css as well. Its one tour case ("tour entry without a selected lesson...") returns before the layer is appended, so `inertBackground` never runs against the fake DOM. The harness passes with these changes.
4. Verify commands used `--basetemp=work/test-tmp-06-03` instead of the plan's `work/test-tmp-p6`, per exec-rules. The directory has been deleted.
5. No commits, per exec-rules.

## Design hook

The impeccable hook flagged 5 findings in classroom.css at lines 3705, 3876, 3956, 4019 and 4022. They are the pre-existing legacy range (originally 3701 to 4018), shifted by the 4 lines this plan added above it. I left them alone as instructed. The two new rules use only `var(--accent)`.

## Notes for 06-04 (real browser gate)

- Palette shortcut on macOS:
  - Cmd+K opens the palette from the page.
  - Ctrl+K outside the editor does nothing.
  - With focus in `.cm-content`, neither key opens the palette.
  - Check the opposite mapping on Linux/Chromium in the container: Ctrl+K opens the palette and Meta+K does not. The container runs non-Mac, so expect Ctrl.
- Tour:
  - While the tour is open, every `body > *` except `.tour-layer` should have `inert`.
  - Tab should cycle only the tour buttons.
  - After End tour or Esc, no element should still be inert, and focus should return to the opener.
- Skip to result is the second Tab stop from page load:
  - On a runnable lesson, Enter should focus `#results-title`.
  - On a reading or not-ready lesson, where 06-01 hides `#runtime-results`, Enter should focus `#capability`.
  - On the home view, both targets may be hidden and focus stays put. This is a known limitation worth checking.
- `#run[disabled]` should expose the `#capability` text as its accessible description.
- In the focus walk, the palette field and `.manual-parts li` should show the accent cue. The contrast is proven offline at 3:1 or better against both `--surface` and `--tint` in both themes.

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: tests/test_classroom_keyboard.py and all four modified assets (git diff --stat shows each).
- No commits to check, because the orchestrator commits.
