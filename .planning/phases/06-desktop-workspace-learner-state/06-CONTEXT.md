# Phase 6 context: desktop workspace and learner state

**Phase goal (ROADMAP):** Learners can operate the desktop classroom confidently
across its real lesson modes and continue their work without accidental
execution or loss of saved evidence.

**Requirements:** UX-01, UX-02, STATE-01 (`.planning/REQUIREMENTS.md`).

**Source of findings:** `06-RESEARCH.md` in this directory. Its file:line hooks
were re-checked against the tree on 2026-11-23 (for example `showCapability`
at `src/ds60sqlpy/assets/classroom.js:1501`, `resetResult` at 1572, the backup
restore at 1313-1342, `stashDraft` at 620, `showJob` at 2851,
`showLegacyResult` at 3077, the shell shortcut listener at
`classroom-shell.js:297-311`, the tour at `classroom-guide.js:604-735`).

**Decision source:** autopilot. The user approved the requirements earlier and
stated "desktop only, no mobile". The orchestrator supplied the locked
decisions below.

## Decisions (LOCKED)

- **D-01 axe-core is approved.** Fetch exactly axe-core 4.14.1 (the newest
  4.14.x on the configured feed on 2026-11-23; registry integrity
  `sha512-FHfa+lmNjQZfJz1q8wKqIDwC6DExcHt/pkjNQb09a3NPjCKg2rhu5qb2S4r76ASyFNNtuFooJpZe37OgudVGtQ==`,
  MPL-2.0, repository `github.com/dequelabs/axe-core`, no postinstall) with
  `npm pack --ignore-scripts` through the feed proxy already set in `~/.npmrc`
  (`https://packagefeedproxy.microsoft.io/npm/`). Store it only under
  `~/.cache/ds60sqlpy/axe`, verify the tarball against the recorded integrity,
  and write a provenance file next to it. Never place it in the repository, a
  repository `node_modules`, or a lockfile. The gate injects it from a
  read-only mount. The gate fails on `serious` or `critical` violations and
  records `moderate` and `minor` ones as advisory. This decision is the human
  approval that the research's `[SUS]` legitimacy verdict asked for; the fetch
  task still verifies integrity before use.
- **D-02 Module drafts keep a single slot.** Draft history is deferred. The
  browser-backup fingerprint fix (06-02) closes the known loss path.
- **D-03 No readiness cue in the lesson list.** UX-01 covers the workspace only.
- **D-04 Phase 1 first-time clarity UAT is folded into 06-04** as a final,
  non-blocking human verification item recorded as `human_needed`. Autonomous
  execution must not wait for it.
- **D-05 Desktop only, American English, no em or en dashes.** No responsive or
  mobile work. Leave the existing 390px Phase 1 check untouched. No U+2013 or
  U+2014 in any UI copy, test, plan or summary written by this phase. The
  middle dot separator already used in the UI is allowed.
- **D-06 Tooling location and container hygiene.** Browser and test tooling
  runs only in containers or under `~/.cache/ds60sqlpy`. Install nothing into
  the repository. Never touch containers named `ds60-classroom*`,
  `awesome-copilot*`, `tender_feistel` or `condescending_kirch`. Disposable
  stacks use the `ds60-phase6-` prefix (this phase uses
  `ds60-phase6-browser`), are driven with `docker compose -p ds60-phase6-...`
  (or the launcher's `--project ds60-phase6-browser`), and end with
  `down -v` for that project only.
- **D-07 Exact-string tests stay exact.** When copy changes, the plan updates
  the asserting test to the new exact string on purpose (for example the
  harness check count in `tests/test_module_ui.py`, the not-ready sentence at
  `scripts/check_classroom_ui.mjs:2467`, and the `Saved run` assertions).
  Never loosen an equality into a substring or regex to make a change pass.
- **D-08 Concurrent content work is off limits.** Phase 6 plans must not edit
  `courses/*`, `src/ds60sqlpy/catalog_builder.py`,
  `scripts/build_coverage_matrix.py`, `tests/test_coverage_matrix.py` or
  `src/ds60sqlpy/module_extensions.py`. The browser gate picks sample lessons
  by `runtime_profile` at run time. If the subject chooser baseline drifts
  because of content edits, the plan only rebuilds the disposable image from
  the current tree so the gate's derived `SUBJECTS` set matches; it never
  edits content to make the gate pass.

## The agent's discretion (choices made by the planner)

- **Mode descriptor shape.** One pure function `workspaceMode(lesson, cap)`
  in a marked block `// BEGIN WORKSPACE MODE PURE HELPERS` and
  `// END WORKSPACE MODE PURE HELPERS` in `classroom.js`, tested from pytest
  through a Node vm (the existing `tests/test_learning_editor.py` pattern,
  skipped when Node is absent). Kinds: `draft`, `reading`, `save-only`,
  `browser`, `python`, `sql`, `worker`.
- **Where mode information renders.** A new `<dl id="workspace-mode">` directly
  under `#capability` with three rows: "Lesson type", "Code runs in",
  "Results appear in". `#capability` stays the readiness line, so the exact
  not-ready sentence is unchanged.
- **Reading, draft and save-only lessons hide the Result panel** with the
  `hidden` attribute (never CSS only).
- **Old module jobs** use the same "Saved run from <time>. It keeps the code
  that produced it, so opening it later never changes your editor." sentence
  as legacy receipts.
- **Backup conflict handling** stores a fingerprint inside the existing stash
  object (extra `stash_meta` key, so existing `.source` readers keep working),
  and moves a conflicting backup to `ds60.classroom.conflict.<key>` so ordinary
  autosave can never silently delete it. Choices: "Use browser copy",
  "Keep saved draft" (dismiss for now, the copy stays offered), "Discard
  browser copy" (native confirm). The server does not expose a draft
  `updated_at`, so the fingerprint is the SHA-256 of the server fields the
  page loaded; the stash also records its own `saved_at` for display.
- **Palette shortcut rule.** macOS: Cmd+K only. Other platforms: Ctrl+K only.
  Never when the event target is inside `.cm-editor`. The `/` shortcut is
  unchanged.
- **Tour modality** uses the `inert` attribute on every other direct child of
  `<body>` while the tour layer is mounted (the layer is appended to `<body>`,
  so it is never inside an inert subtree).
- **Desktop jump to Result** is a second skip link, "Skip to result", that
  focuses `#results-title`, or `#capability` when the lesson has no Result
  panel.
- **The language badge (`#language`, research gap G6) is left as is.** The new
  mode strip carries the readable lesson type, and the gate already reads the
  badge.
- **Gate code layout.** New Phase 6 browser flows live in a new module
  `scripts/check_classroom_workspace.py`, called from
  `scripts/check_classroom_browser.py`, so the existing 1074-line checker only
  gains wiring.
- **Native `confirm` and `prompt` dialogs stay** (research K7); the gate
  handles them with `page.on("dialog")`.

## Deferred ideas (OUT OF SCOPE)

- Mobile or narrow layouts.
- Module draft version history (D-02).
- Lesson-list readiness cues (D-03).
- The CodeMirror UTF-16 versus code-point cursor offset item from Phase 1.
- Replacing native confirm and prompt dialogs.
- Any edit under the D-08 paths.

## Canonical references

- `06-RESEARCH.md` (this directory)
- `AGENTS.md:150-160` (save before context change, history never reruns)
- `src/ds60sqlpy/assets/classroom.js`, `classroom-shell.js`,
  `classroom-guide.js`, `classroom.css`, `classroom.html`
- `scripts/check_classroom_ui.mjs` (95 checks at HEAD, pinned in
  `tests/test_module_ui.py:30`)
- `scripts/check_classroom_browser.py`, `tests/test_classroom_browser_probe.py`
- `~/.cache/ds60sqlpy/run-browser.sh` (gate wrapper, outside the repo)
