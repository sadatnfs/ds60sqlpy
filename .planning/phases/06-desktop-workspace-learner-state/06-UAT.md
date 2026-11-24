---
status: human_needed
phase: 06-desktop-workspace-learner-state
source: [06-04-PLAN.md]
blocking: false
started: 2026-11-24T04:50:00Z
updated: 2026-11-24T04:50:00Z
---

# Phase 6 Human UAT

These checks need a person. They do not block plan 06-04 (D-04). The automated
browser gate (scripts/check_classroom_browser.py with scripts/check_classroom_workspace.py)
covers the mode strip, keyboard flow, focus, axe-core scans, draft preservation and
restart recovery in real Chromium. Record pass or issues under each item.

Use a disposable classroom on a desktop browser. Never use the real `ds60sqlpy` stack.

## Current Test

number: 1
name: First-time clarity walkthrough on a fresh desktop browser (D-04)
awaiting: user response

## Tests

### 1. First-time clarity walkthrough on a fresh desktop browser (D-04)
status: pending
steps: |
  Use a fresh browser profile with no saved classroom data. Without coaching:
  open the home page, pick a first lesson, and find where to type the answer.
  Run it and read the result. Then open a reading lesson and say what the
  workspace strip means: what kind of lesson it is, where code runs, and where
  results appear.
expected: |
  The reviewer finds the editor, Run and the result without help. They also
  understand from the strip that a reading lesson runs no code and has no
  Result panel.
result:

### 2. Screen reader spot check
status: pending
steps: |
  With VoiceOver on macOS or NVDA on Windows, open a lesson whose runtime is not
  ready and move to the disabled Run control and its explanation. Then make a
  browser copy conflict: a saved draft plus a different unsaved browser copy for
  the same lesson. Move through the "Use browser copy", "Keep saved draft" and
  "Discard browser copy" panel.
expected: |
  The reader announces why Run is unavailable and what to do next. The choice
  panel announces its message and each button by name, and neither choice
  changes the draft until it is confirmed.
result:

### 3. macOS Cmd+K command palette
status: pending
steps: |
  On a real Mac, press Cmd+K in the classroom outside the code editor. Type part
  of a lesson title and press Enter. Press Cmd+K again inside the code editor.
expected: |
  Outside the editor the palette opens and Enter goes to the lesson. Inside the
  editor the shortcut does not open the palette, so editing is not interrupted.
result:

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0

## Gaps

None recorded yet.
