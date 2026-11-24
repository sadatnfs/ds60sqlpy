---
phase: 06-desktop-workspace-learner-state
plan: 02
subsystem: classroom-ui
status: complete
requirements: [STATE-01]
tags: [drafts, localStorage, state, harness]
requires: ["06-01"]
provides:
  - "DRAFT BACKUP pure block (draftFingerprint, backupFields, backupDecision) in classroom.js"
  - "Fingerprinted browser backups (stash_meta: base_sha256, saved_at, origin)"
  - "Conflict store ds60.classroom.conflict.<key> and the #draft-conflict choice panel"
affects: [06-04]
tech-stack:
  added: []
  patterns: ["synchronous cyrb53 change detector for draft bases", "marked pure helper block evaluated alone in a Node vm by pytest"]
key-files:
  created:
    - tests/test_draft_backup.py
  modified:
    - src/ds60sqlpy/assets/classroom.js
    - scripts/check_classroom_ui.mjs
    - tests/test_module_ui.py
decisions:
  - "Harness baseline was 105 after 06-01, so the pin is 110 (exactly 5 new checks), not the plan's 105."
  - "conflictPinned is a Map (key to in-memory conflict list) instead of a Set, so a backup that could not be written to the conflict store is still offered in this session."
  - "The panel is tracked in a module variable and inserted with save-state.before(panel); it is not looked up with getElementById."
  - "Grammar: one remaining extra entry reads '1 more browser copy is also kept.'; two or more use the plan's plural sentence."
metrics:
  completed: 2026-11-23
actuals:
  tasks: 3
  commits: 0
  note: "The orchestrator makes commits under exec-rules. This executor made none, so plan_head_before/after are not recorded."
---

# Phase 6 Plan 02: Draft backup fingerprint and history safety Summary

A stale browser backup can no longer silently replace a newer server draft. Every backup now records the fingerprint of the server draft it was based on. When a lesson opens, the backup is restored automatically only if that base matches the draft just loaded. A backup identical to the server draft is dropped silently. Any other backup, including old unfingerprinted ones, is moved to a separate conflict store and offered through a choice panel. The server draft stays in the editor and nothing autosaves. The harness also proves that clicking a module Saved runs entry starts no request at all (research gap T1).

## What was done

**Task 1 (tracer: fingerprinted stash and decision helper).**
- Added `// BEGIN DRAFT BACKUP PURE HELPERS` / `// END ...` directly after the workspace mode block. It contains:
  - `draftFingerprint(fields)`: cyrb53 with seed 0 over `JSON.stringify(fields)`, returned as hex.
  - `backupFields(backup)`: a copy without `stash_meta`.
  - `backupDecision(backup, serverFields)`: returns none, discard, restore or conflict. A backup is "none" unless source, prediction and explanation are strings of at most 2,000,000 characters.
- `stashBases` Map. `stashDraft` writes `{...fields, stash_meta: {base_sha256, saved_at, origin: "browser-backup"}}`, so existing readers of `.source` are unaffected.
- `openLesson` captures `serverFields = values()` and records its fingerprint as the base before reading the stash. Then:
  - restore: same apply path as before. The notes and evidence part moved into `applyDraftNotes(entry)` and behaves the same.
  - discard: both stash keys are removed.
  - none: nothing changes.
- `queueSave` success sets `stashBases.set(context.key, draftFingerprint(fields))`.
- Added `tests/test_draft_backup.py`, which runs 5 vm tests against the marked block.
- Tracer gate: the verify command passed (21 tests) before expanding.

**Task 2 (conflict store and panel).**
- `readConflicts` keeps only valid entries, at most 5, newest first. `writeConflicts` removes the key when the list is empty and returns false on a storage error.
- If moving the backup to the conflict store fails, the unsaved stash is left in place, the list is kept in memory (`conflictPinned`), and `queueSave` skips the stash removal for that key.
- On every open, conflict entries equal to the server draft are dropped. The panel renders if any entries remain.
- `renderDraftConflict(key)` builds `div#draft-conflict.notice.warn` with `role="group"`, `aria-labelledby="draft-conflict-text"` and `data-key`, using `node()` and `textContent` only. It goes immediately before `#save-state`. The copy and the three buttons follow the plan: "Use browser copy" (or "Use previous draft"), "Keep saved draft" and "Discard browser copy". The time is shown as `toLocaleString()` of a parsed `saved_at`, or "an earlier visit".
- Use: confirm, `flushSave()`, `sameView` check, then the current fields are kept as a "replaced-draft" entry. After that the code calls `replaceSource`, `applyDraftNotes`, `markDirty` and re-renders the panel. Status shows "The browser copy is in the editor and is being saved." and then `flushSave()` saves the chosen copy.
- Keep: removes the panel and shows the exact save-state sentence. The stored list is unchanged.
- Discard: deletes the first entry only after a native confirm, then re-renders.
- The panel is removed in `showHome` and for planned lessons. `openLesson` always re-renders it for the new key.

**Task 3 (harness).**
- Updated (D-07): "old module browser drafts recover..." is now "old module browser drafts are offered, not forced, without losing notes". It checks that:
  - the server source is in the editor
  - the panel is present
  - no module-save is sent
  - the legacy key moved to the conflict store
  - "Use browser copy" restores the source and explanation, a module-save carries them, and the old server draft is kept as replaced-draft.
- New checks:
  1. stale fingerprinted backup: no overwrite and no save timer, plus the exact panel text and button order, and that discard is refused or accepted through confirm
  2. a matching base restores, with the exact "Recovered a browser draft..." sentence
  3. an equal backup is discarded silently
  4. Keep leaves the copy offered again on the next open, with the exact "an earlier visit" text
  5. a module Saved runs click sends no run or step request, and in fact no request at all
- Fingerprints in tests come from `e.run("draftFingerprint(...)")`, not hardcoded hashes.
- The fake `Element` gained `before()` and `remove()` so the panel insertion can be observed.
- `tests/test_module_ui.py` is pinned at `{"checks": 110, ...}`.

## Verification (real output)

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-06-02 tests/test_draft_backup.py tests/test_workspace_mode.py -q` (Task 1 tracer) | 21 passed |
| `node scripts/check_classroom_ui.mjs` after Task 2, before Task 3 | stopped at the old silent-recovery test (expected `old retained source`, got `llm-002`), as the plan predicted |
| `node scripts/check_classroom_ui.mjs \| tail -1` | `{"checks":110,"passed":true,"final":true}` |
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-06-02 -q tests/test_module_ui.py tests/test_draft_backup.py tests/test_workspace_mode.py tests/test_learning_editor.py` | 23 passed |
| same with `tests/test_unified_classroom.py tests/test_classroom_http.py` | 24 passed |
| `.venv/bin/ruff check tests/test_draft_backup.py tests/test_module_ui.py` | All checks passed! |
| `.venv/bin/ruff format --check tests/test_draft_backup.py tests/test_module_ui.py` | 2 files already formatted |
| `.venv/bin/mypy src` | Success: no issues found in 62 source files |
| perl dash scan on classroom.js, test_draft_backup.py, check_classroom_ui.mjs, test_module_ui.py | no output, exit 0 |
| `grep -c "// BEGIN DRAFT BACKUP PURE HELPERS" classroom.js` | 1 |
| `grep -c "stash_meta" classroom.js` | 8 |
| `grep -c '"ds60.classroom.conflict."' classroom.js` | 1 |
| `grep -c '"checks": 110' tests/test_module_ui.py` | 1 |
| added `innerHTML` lines in the classroom.js diff | 0 |
| Mutation check: history click also calls `runCode()` (scratch copy) | harness fails on the new T1 check (a `module-save` started) |
| Mutation check: `backupDecision` returns restore instead of conflict (scratch copy) | harness fails on the updated offered-not-forced check |

The mutation copies were scratch files under work/06-02 and have been deleted. No real browser run was done. Plan 06-04 owns the browser gate.

## Deviations from Plan

1. **[Concurrent baseline] Pin 110, not 105.** 06-01 already raised the harness to 105. I added exactly 5 checks and updated 1.
2. **[Rule 1] The T1 check is stricter than the plan.** A plain `/run|step/` filter missed a mutated history click that calls `runCode()`, because a run waits on a draft save first. The check now also asserts that no request of any kind starts.
3. **[Rule 2] `conflictPinned` is a Map holding the list in memory**, so a backup that could not be written to storage is still offered in this session instead of being lost when the next edit overwrites the unsaved stash.
4. **Harness fake DOM:** `Element.before()` and `Element.remove()` were added to `check_classroom_ui.mjs`. No HTML or CSS changes (06-03's files untouched); the panel reuses the existing `.notice.warn` styles.
5. **Grammar:** a single extra entry reads "1 more browser copy is also kept."
6. **Basetemp:** I used `work/test-tmp-06-02` per the orchestrator rules, not the plan's `work/test-tmp-p6`.
7. **Process:** one edit to classroom.js (tracking the panel in a variable) used a short Python read-replace-write with an exact single-match assert instead of the edit tool. It ran immediately after a read, and every later edit used the edit tool.

## Notes for 06-04

- The panel is `#draft-conflict`, inserted as the previous sibling of `#save-state`, with buttons in this order: "Use browser copy" or "Use previous draft", then "Keep saved draft", then "Discard browser copy". Use and Discard open native confirm dialogs, so the browser gate must handle `page.on("dialog")`.
- To reproduce a conflict in a real browser, seed `localStorage["ds60.classroom.unsaved.<key>"]` with `{source, prediction, explanation}` and no `stash_meta` (or a wrong `base_sha256`), then open the lesson. Expect the server source in the editor and `localStorage["ds60.classroom.conflict.<key>"]` to hold the copy.
- Backups now carry `stash_meta`, so any browser-gate assertion that compares a whole stash JSON must ignore that key.
- The panel inherits `.notice.warn`. I did not do a visual check of button spacing inside the notice; 06-03 or 06-04 may want a small CSS rule.

## Known Stubs

None.

## Threat Flags

None. New surface is localStorage only and is covered by T-06-03 to T-06-05.

## Self-Check: PASSED

- FOUND: tests/test_draft_backup.py
- FOUND: BEGIN/END DRAFT BACKUP PURE HELPERS markers in classroom.js
- FOUND: `"checks": 110` in tests/test_module_ui.py
- Commits: none by design (the orchestrator commits).
