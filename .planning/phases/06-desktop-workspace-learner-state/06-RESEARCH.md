# Phase 6: Desktop Workspace & Learner State - Research

**Researched:** 2026-11-18
**Domain:** Classroom browser UI (vanilla JS, CodeMirror 6, CSS tokens), learner state stores, containerized Playwright gate
**Confidence:** HIGH for the code audit (every claim cites a file read this session). MEDIUM for adding axe-core to the gate (the legitimacy seam returned SUS).

<user_constraints>
## User Constraints

No `06-CONTEXT.md` exists. These constraints come from the orchestrator prompt and from the locked decisions in `.planning/STATE.md`. Treat them as locked.

### Locked Decisions
- **Desktop only.** Do not design or test mobile layouts. Leave the existing 390px check in the Phase 1 gate as it is, and add nothing for narrow viewports.
- **Language and punctuation.** Write in American English. Use no em dashes or en dashes in any written artifact: UI copy, docs, plans or tests.
- **Where tooling runs.** Browser and test tooling runs in containers or in external caches under `~/.cache/ds60sqlpy`, never in the repo or OneDrive. Install no packages into the repo.
- **Disposable gate target.** Browser gates run only against a disposable project. Phase 1 used `ds60-phase1-browser`. Never point a gate at the learner project `ds60-classroom` or its volumes.
- **Preserve learner state.** Drafts, progress and receipts survive every navigation. Viewing old evidence never re-executes code. This comes from STATE.md and also from the AGENTS.md invariants listed below.
- **Build on Phase 1.** Phase 1 shipped the manual page, step-through UI, guided tour and browser gate. Prefer focused, verifiable changes over a redesign.

### the agent's Discretion
- How the mode descriptor is structured and where it renders.
- Which keyboard and focus fixes to make, as long as the UX-02 checks pass.
- Whether to add axe-core to the containerized gate. It is recommended, behind a human checkpoint.

### Deferred Ideas (OUT OF SCOPE)
- Mobile or narrow layouts.
- Draft version history for module lessons. This is listed as an open question, not a Phase 6 deliverable.
- The Phase 1 open item where the CodeMirror cursor offset counts UTF-16 units but the server counts code points.
- Files that other agents are editing at the same time. Phase 6 plans must not touch them:
  - `courses/*`
  - `scripts/build_coverage_matrix.py`
  - `tests/test_coverage_matrix.py`
  - `src/ds60sqlpy/catalog_builder.py`
  - `src/ds60sqlpy/module_extensions.py`
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| UX-01 | In each supported desktop lesson mode, the workspace clearly identifies the current lesson, available actions, runtime or reading capability, readiness, and where results appear. | Mode matrix (Q1), gaps G1 to G8, the pure `workspaceMode()` descriptor pattern, Plan 06-01 |
| UX-02 | A learner can operate the desktop classroom with the keyboard and see clear focus and status cues; applicable project contrast and accessibility checks pass. | Keyboard and focus audit (Q2), gaps K1 to K7, contrast table, Plan 06-03, and the gate checks in Plan 06-04 |
| STATE-01 | Navigation, lesson switching, viewing old results, test setup, and runtime restart preserve learner drafts, progress, and receipts; viewing old evidence never re-executes code. | State audit (Q3), which found no re-execution path, draft-loss risk S1 (a stale browser backup), Plans 06-02 and 06-04 |
</phase_requirements>

## Summary

The classroom already has most of what Phase 6 needs. Saves flush before every context change. Receipts are append-only. Viewing old runs only displays them, on both the legacy and module engines. Phase 1 also shipped a skip link, a global `:focus-visible` ring, a native `<dialog>` palette, a guided tour with a focus trap, a manual with a keyboard table, and a containerized Playwright gate that hashes the pad before and after each check.

The gaps are narrow.

**UX-01.** Two routines write the copy for all of the roughly 14 lesson modes: `showCapability` (classroom.js:1501-1570) and `resetResult` (classroom.js:1572-1593). As a result:
- Reading lessons, 348 of them in the live catalog, still show an empty Result panel that says "Press Run code".
- Ready module lessons drop the runtime detail, so the learner never learns where the code runs.
- Browser previews are labeled as if they ran on the server.

**UX-02.** Three issues stand out:
- The tour dialog claims `aria-modal` but leaves the background focusable.
- The palette search input has no focus indicator.
- On macOS, the capture-phase Ctrl+K listener steals CodeMirror's Ctrl-k binding.

No gate runs an axe scan or a keyboard-only walk.

**STATE-01.** No path re-executes code from history. The one real draft-loss path is the localStorage backup restore at classroom.js:1313-1342. It overrides the server draft without checking whether the server draft changed after the backup was taken. Module drafts are single-slot (modules.py:360-437), so the overwritten version is lost for good.

**Primary recommendation:** Make four focused changes.
1. Add one pure, unit-tested `workspaceMode(lesson, capability)` descriptor. It drives the capability strip, the Run label, the empty-result copy and whether the results panel is visible.
2. Fingerprint the browser draft backup, and ask the learner before it overrides a server draft that has changed.
3. Fix the three keyboard issues.
4. Extend the existing containerized gate with a sample of lesson modes, a keyboard-only flow, an axe scan and preservation receipts.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Mode descriptor (lesson kind, action, location, empty-result copy) | Browser / Client (classroom.js) | API (module_service.py payload, unchanged) | The payload already carries `engine`, `runtime_profile`, `execution_mode` and `capability`. A pure client function avoids a server schema change. |
| Readiness truth | API / Backend (module_jobs.py:142-170, capabilities.py) | Client renders it | The server owns readiness. The client must not infer it. |
| Keyboard, focus and contrast | Browser / Client (HTML, CSS, shell, guide, editor bridge) | none | Pure presentation. |
| Drafts, progress, receipts, job history | Database / Storage (`.learning/*` files written by the server) | Browser localStorage backup | The server is the source of truth. localStorage is only a crash backup. |
| Backup conflict decision | Browser / Client | none | Only the client sees both the stash and the server draft it just loaded. |
| Evidence of no re-execution | Test tier (browser gate) | pytest | The gate records request logs and the pad SHA-256 before and after each check. |

## Project Constraints (from copilot-instructions.md and AGENTS.md)

- Save drafts before any context change. Navigation, reload, Stop and history must never silently resume a run (AGENTS.md:150-160).
- Opening a past result must never rerun code or replace the pad (AGENTS.md:150-160). The existing gate enforces this with `assert_no_execution_requests` (check_classroom_browser.py:297-301).
- A "ready" DAX status does not authorize Run. Draft mode hides Run (classroom.js:1511-1514).
- Build new UI text with `textContent` and `node()`, the existing pattern. The only HTML path is server-produced syntax highlighting (`highlightedSourceBlock`, classroom.js:3069).
- Run tests with `.venv/bin/python -m pytest -n 4 --dist loadgroup` (Makefile:1-2 and 53-54). Run the UI harness with `node scripts/check_classroom_ui.mjs` (Makefile:81).
- Use no em or en dashes in copy. The existing UI separates items with the middle dot `·` (classroom.js:1346), which is allowed.

## Standard Stack

Phase 6 needs no new runtime packages. Everything ships with the existing assets.

### Core (already present)
| Library | Version | Purpose | Evidence |
|---------|---------|---------|----------|
| CodeMirror 6 (`@codemirror/view`) | 6.43.15 | Editor, keymap, tab focus mode | [VERIFIED: scripts/codemirror-bundle/package.json `"@codemirror/view": "6.43.15"`] |
| Native `<dialog>` with `showModal()` | browser built-in | Palette modal with a native focus trap and focus return | [VERIFIED: classroom.html:1251 `<dialog id="palette" class="palette" aria-label="Search lessons and subjects">`] |
| Playwright Python | 1.64.1. Container image `mcr.microsoft.com/playwright/python:v1.64.1-noble`, libraries at `~/.cache/ds60sqlpy/linux-pw` | Containerized browser gate | [VERIFIED: ~/.cache/ds60sqlpy/run-browser.sh, `docker images`] |
| Node fake-DOM harness | node v26.13.0 | 95 deterministic UI tests | [VERIFIED: scripts/check_classroom_ui.mjs, `node --version`] |
| Pure helper extraction | n/a | pytest evaluates marked helper blocks in a Node vm | [VERIFIED: tests/test_learning_editor.py:17-43, which splits on `// BEGIN DIAGNOSTIC PURE HELPERS` and `// END DIAGNOSTIC PURE HELPERS`] |

### Supporting (test-only, external cache)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| axe-core `axe.min.js` [ASSUMED] | 4.14.1 per `npm view` | WCAG rule scan inside the Playwright gate | Plan 06-04 only. Cache it under `~/.cache/ds60sqlpy/axe/` and mount it read-only. Never add it to the repo or a lockfile. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Injecting the axe-core script | `@axe-core/playwright` (npm 4.14.0) or `axe-playwright-python` (PyPI 0.1.8) | Both need an install inside the container on every run. Injecting the one cached file with `page.add_script_tag(path=...)` needs no install. The CSP allows it: a curl of the disposable stack shows `script-src 'self' 'unsafe-inline'`. |
| Custom ARIA rule checks | axe-core | Hand-written rules miss most WCAG checks. Keep custom checks only for what axe cannot see: focus ring visibility, tab order and shortcut behavior. |

**Installation:** nothing goes into the repo. After a human checkpoint, Plan 06-04 fetches axe into the external cache:
```bash
mkdir -p ~/.cache/ds60sqlpy/axe && cd ~/.cache/ds60sqlpy/axe && npm pack axe-core@4.14.1 && tar -xzf axe-core-4.14.1.tgz package/axe.min.js package/LICENSE
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| axe-core | npm | unknown (the seam returned null signals) | unknown | `npm view` reports `https://github.com/dequelabs/axe-core.git`, MPL-2.0, no postinstall | [SUS]. Seam reasons: `unknown-age`, `unknown-downloads`, `no-repository` | Flagged. The planner must add `checkpoint:human-verify` before the fetch. |

**Packages removed due to [SLOP] verdict:** none

**Packages flagged as suspicious [SUS]:** axe-core. The seam could not reach registry metadata, so every signal was null, while `npm view` through the configured feed returned version 4.14.1, an MPL-2.0 license, the dequelabs repository and an empty postinstall. The verdict reflects a lookup gap rather than a red flag, but the rule still applies. Fallback if the human declines: run the gate without axe and rely on the custom keyboard, focus and contrast checks.

## Q1. Lesson Modes and UX-01 Gaps

### Live catalog census
I read the catalog from the disposable stack with a read-only `curl` POST to `classroom-index`. It reported 40 tracks and no planned lessons. These counts are a snapshot: other agents are editing `courses/*` right now, so plans must pick lessons by profile, not by hardcoded counts.

| Engine | Mode | Profiles (count, example) |
|--------|------|---------------------------|
| legacy | Python pad: scripts, plus `.ipynb` files run as `# %%` cells (capabilities.py:291-305) | python (115, python-01) |
| legacy | SQL, as a snippet or a whole lesson through psql. Whole lesson is the default for `.sql` paths (capabilities.py:244-290). | sql (86, sql-start-01) |
| legacy | Reading runner (`none`) and save-only runners (`cpp`, `scala`, `kubernetes`) | 0 lessons today, but the code path is live (curriculum_framework.py:34-42) |
| module | Reading | reading (246 practice + 102 tutorial; k8s-001, asm-018) |
| module | Worker run | python-core (246), data-engineering including dbt (91), r-statistics (108) and llm-torch-cpu (81). Also: python-web, data-platforms-python, javascript-node, typescript-node, php-cli, c17, cpp20, csharp-dotnet, go, rust-stable, swift-linux, java21, julia, jax-cpu, tensorflow-cpu, scala-jvm, spark-local-scala and spark-local-python. |
| module | Worker run, long or heavy | stan-cpu (8, bayes-017), bayesian-cpu (9, bayes-009), k8s-kind cluster (12, k8s-003) |
| module | Worker run, GPU | None in the catalog. The code supports cuda-cpp, cuda-python, pytorch-cuda and tensorflow-cuda, adding `--gpu-device 0` to their setup commands (module_service.py:296-308, module_jobs.py:25-58). |
| module | Browser preview | html-browser (30, web-001), javascript-browser (24, js-043) |
| module | Offline draft | dax-offline (60, dax-001) |

The disposable stack runs only `python-core-worker`, so every other worker profile shows the not-ready state. That makes the stack a good fixture for testing not-ready copy.

### What the workspace shows today
Sources: classroom.js:1501-1593, 1133-1169 and 1346.

Every mode shows the same identity elements:
- `#badges` and `h1#title` (html:166-167)
- `#language`, built as `data.language + (data.runtime_profile !== data.language ? " · " + data.runtime_profile : "")` [VERIFIED: classroom.js:1345-1346]
- `#capability` (html:180)

| Mode | Capability text (verbatim source) | Run control | Empty result copy | Results location |
|------|-----------------------------------|-------------|-------------------|------------------|
| Legacy Python or SQL, ready | `"Ready to run in your local classroom. " + (current.engine === "legacy" ? cap.detail \|\| "" : "")` [VERIFIED: classroom.js:1532-1533] | `"Run code"`, runner select, timeout | `"No run yet. Press Run code to try this lesson."` [VERIFIED: classroom.js:1581] | `#runtime-results` (html:635): `#output`, `#checks`, `#sql-results`, `#figures`, and Saved runs in `#job-history` (html:672) |
| Legacy save-only runner | Uses the not-ready branch: "The ... runtime is not ready." | Disabled. The option label adds " (save only)" (classroom.js:1143-1147). | Same "Press Run code" copy | Same panel, never filled |
| Legacy reading (`none`) | Source section hidden (classroom.js:1139) | Hidden along with the source section | Same panel | Same panel |
| Module worker, ready | `"Ready to run in your local classroom. "`, with the module detail dropped [VERIFIED: classroom.js:1532-1533] | `"Run code"` | Same | Same panel. History comes from `jobs.history`, 30 newest (module_jobs.py:621-632). |
| Module worker, not ready | `"The "` + `<code>profile</code>` + `" runtime is not ready. " + (cap.detail \|\| "") + activity` [VERIFIED: classroom.js:1522-1527], with class `notice warn` | Disabled | Same "Press Run code" | Same panel, plus the `#runtime-setup` commands |
| Module browser | Same ready text as a worker. `browser_capability` sets `execution_location` to browser (browser_runs.py:27-40), but the client never shows it. | `"Run browser preview"` [VERIFIED: classroom.js:1547-1548] | Same "Press Run code", which names the wrong button | The preview frame (`#browser-live-state`, html:436) plus observation history (limit 20) |
| Module reading | `"Read the guide and record your reasoning. This lesson needs no code runtime."` [VERIFIED: classroom.js:1531] | Disabled, labeled `"Reading and reasoning"` [VERIFIED: classroom.js:1543-1544] | Same "Press Run code" | `#runtime-results` and Saved runs stay visible but can never fill |
| Module DAX draft | `cap.detail`: "Offline DAX pad: save, compare and export code..." (module_drafts.py:18-28) | Run, Refresh and the results panel are hidden [VERIFIED: classroom.js:1511-1514] | Not shown | The `#offline-workspace` comparison |

### UX-01 gaps (ranked)
- **G1 (high): Reading lessons promise a run.**
  - `resetResult` always writes `"No run yet. Press Run code to try this lesson."`.
  - It also writes the output note `"Press Run code. What your program prints, and any error messages, appear here."` [VERIFIED: classroom.js:1581-1582, html:652].
  - For 348 reading lessons, Run is disabled, yet the Result panel and Saved runs stay visible.
  - Only draft mode hides `#runtime-results` (classroom.js:1513).
- **G2 (high): Ready module lessons do not say where code runs.** The module `cap.detail` is discarded (classroom.js:1532-1533), so a learner cannot tell a worker container from the browser sandbox.
- **G3 (medium): Browser previews use server-run copy.** The empty result says "Press Run code" while the button says "Run browser preview". Results also appear in the preview frame, not the console.
- **G4 (medium): Save-only legacy runners read as "not ready".** The learner is told to prepare a runtime that does not exist. The copy should say "save only".
- **G5 (medium): Old module runs are not labeled as old.**
  - Legacy receipts already say this: `"Saved run"` plus `" from "` and the time, then `". It keeps the code that produced it, so opening it later never changes your editor."` [VERIFIED: classroom.js:3093-3097, in `showLegacyResult` at 3077].
  - Module `showJob` (2851) keeps the title `"Result"` (2873) and shows only status text, so an old job looks like the current result.
- **G6 (low): The language badge shows raw IDs.** `#language` shows strings like `dax · dax-offline` (classroom.js:1345-1346) instead of a readable label.
- **G7 (low): The Run button does not explain why it is disabled.** `#run` has `aria-keyshortcuts` (html:552) but no `aria-describedby` that points at `#capability`.
- **G8 (low): The two reading modes use different layouts.** Legacy reading hides the source section (classroom.js:1139). Module reading keeps a `"Worksheet"` editor (classroom.js:1550). Keep both layouts, because the module worksheet is where the learner's reasoning is saved, and make the copy consistent instead.

Readiness cues in the lesson list are out of scope for UX-01, which covers the workspace only.

## Q2. Keyboard, Focus and Accessibility Audit

### Present and working (keep)
| Feature | Evidence |
|---------|----------|
| Skip link to `#main` | html:39 `<a class="skip" href="#main">Skip to learning content</a>`, CSS at classroom.css:254-266 |
| Global focus ring | classroom.css:154-157 `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }`. The ring's contrast is 7.69:1 on the light `--bg` and 8.94:1 on the dark one (computed this session). |
| No ring on programmatic focus targets | classroom.css:158-162 `h1[tabindex="-1"]:focus, main:focus, [tabindex="-1"]:focus:not(:focus-visible) { outline: none; }` |
| Editor focus | A `.code-editor:focus-within` ring (css:1394-1397) replaces `.cm-focused` (css:1405-1407) |
| Live regions | `#status` with `role="status" aria-live="polite"` (html:68); `#save-state` (html:549); `#step-status` (html:604); `#sql-readiness-text` (html:248); `#job-status` with `aria-live="polite"` (html:640) |
| Shortcuts | Ctrl/Cmd+S saves and Ctrl/Cmd+Enter runs (classroom.js:4100-4109). Ctrl/Cmd+K toggles the palette, and `/` opens it when the user is not typing (classroom-shell.js:297-311). CodeMirror consumes `Mod-Enter` so no newline is inserted (`{ key: "Mod-Enter", run: () => true }`, entry.mjs:244), and the document listener then runs the code. A third listener handles Escape for the preview fullscreen (classroom.js:3682-3684). |
| Tab inside the editor | `indentWithTab` (entry.mjs:251). The escape hatch is Escape, then Tab. The default keymap also binds Ctrl-m (Shift-Alt-m on macOS) to toggle tab focus mode [CITED: codemirror.net/examples/tab], and the vendor bundle contains `{key:"Ctrl-m",mac:"Shift-Alt-m",run:...}`. The manual (html:1153-1185) and the `#source-help` copy (classroom.js:1507-1509) document Escape then Tab. |
| Palette | Native modal dialog; listbox with `aria-activedescendant`; arrows, Home, End and Enter; focus return (classroom-shell.js:247-287, `returnFocus` at 250 and 262) |
| Guide panels | Step panel keys (classroom-guide.js:252-268); roving focus across exercise steps (classroom.js:3971-3984); Escape closes run-more (classroom.js:3734-3739); separators respond to arrows, Home and End (classroom-shell.js:350-415, classroom-editor.js:98-170) |
| Reduced motion | classroom.css:3239-3247 and 4086-4091; the shell's result reveal (classroom-shell.js:517-521) |
| Status not shown by color alone | `.notice.warn` adds a red border and tint (css:1028-1034), and the text itself says "is not ready" |

### Gaps
- **K1 (high): The tour dialog is not modal for assistive tech.**
  - It sets `role="dialog"` and `aria-modal="true"` (classroom-guide.js:680-681) and traps Tab manually (line 728).
  - Nothing in the assets sets `inert` on the background. A grep of all three JS files found no match.
  - So screen readers can browse outside the tour, and a mouse click outside it can move focus.
  - Fix: set `inert` on `#main` and the header while the tour is open, and remove it on close. Alternatively, move the tour card into a native `<dialog>` opened with `showModal()`.
- **K2 (medium): The palette search input has no focus indicator.**
  - The `.palette-search input` block sets `outline: none` (classroom.css:2893-2896).
  - No `.palette-search:focus-within` rule exists (grep: no match).
  - Fix: add `.palette-search:focus-within { box-shadow: inset 0 -2px 0 var(--accent); }` or an outline.
- **K3 (medium): Shortcut conflict on macOS.**
  - The capture-phase listener intercepts both Ctrl+K and Cmd+K and calls `stopPropagation` (classroom-shell.js:301-306).
  - The CodeMirror bundle binds `{key:"Ctrl-k",run:...}` in its emacs-style macOS keymap (vendor grep). That binding deletes to the end of the line.
  - So in the editor on macOS, Ctrl+K opens the palette instead.
  - Fix: on macOS, when the event target is inside `.cm-editor`, open the palette only for Cmd+K.
- **K4 (medium): A disabled Run has no accessible reason.** See G7. Add `aria-describedby="capability"` to `#run`.
- **K5 (low): Manual parts show focus with a background tint only.**
  - The rule is `.manual-parts li:focus { outline: none; background: var(--tint); }` (css:3608-3611).
  - The `li` elements are programmatic focus targets (`tabindex="-1"`, html:852).
  - The tint contrasts with `--surface` at 1.16:1 in light mode and 1.24:1 in dark (computed). Both are below the 3:1 non-text guideline.
  - Fix: add a left border in `--accent`.
- **K6 (low): No way to jump to results on desktop.**
  - `.spread-switch` (html:195-199, with "Lesson", "Code" and "Result") is `display: none` except under `@media (max-width: 1099px)` (css:3012-3014, 3038, 3066-3075).
  - Desktop keyboard users must Tab through the editor and its controls to reach the Result panel.
  - Fix: the mode strip from G1 and G2 should include a "Results appear in: Result panel" link that moves focus to `#results-title`.
- **K7 (low, keep as is): Five native `confirm` and `prompt` calls** (classroom.js:1932, 2937, 3836 and 3928; classroom-shell.js:630). They are keyboard accessible, so do not replace them in this phase. The gate must register `page.on("dialog")` to handle them.

### Contrast (computed this session with WCAG relative luminance)
| Pair | Light | Dark |
|------|-------|------|
| `--muted` on `--surface` | #535a68 on #ffffff: 6.93 | #b3b9c6 on #20232b: 7.98 |
| `--muted` on `--bg` | 6.30 | 8.93 |
| `--accent` on `--surface` | 8.46 | 7.99 |
| `--accent` on `--tint` | 7.27 | n/a |
| `--error` on `--surface` | 6.52 | 8.89 |
| `--success` on `--surface` | 5.38 | 10.02 |
| `--tint` vs `--surface` (the K5 focus cue) | 1.16 (fails 3:1) | 1.24 (fails) |

Token values [VERIFIED: classroom.css:12-24 and 66-78]:
- Light: `--bg: #f3f4f7`, `--surface: #ffffff`, `--text: #15181e`, `--muted: #535a68`, `--accent: #2f3fb3`, `--tint: #ebedfb`, `--error: #b4232f`, `--success: #1f7a3a`.
- Dark: `--bg: #17191f`, `--surface: #20232b`, `--text: #eceef3`, `--muted: #b3b9c6`, `--accent: #aab4ff`, `--tint: #2c3150`, `--error: #ffadb3`, `--success: #8fe0a8`.

### Existing automated checks
- **UI harness (scripts/check_classroom_ui.mjs).** It runs inside pytest through tests/test_module_ui.py:15-30. Relevant tests:
  - Escape in the editor lets keyboard users leave it (line 1461).
  - Subject accent contrast of 4.5:1 in four themes (1484-1550).
  - Contrast of the primary button's hover state (1552-1648).
  - Console contrast of 7:1 (1693-1725).
- **Browser gate (scripts/check_classroom_browser.py).** It checks the computed contrast of `#output`, the body and the guide prose against 4.5:1 in both color schemes (603-626). The contrast math itself is tested by tests/test_classroom_browser_probe.py:18-30.
- **Missing:**
  - an axe scan
  - a Tab-order walk
  - a check that each tab stop shows a visible focus ring
  - a keyboard-only end-to-end flow
  - a contrast table covering every token pair

### Checks to add in the containerized gate (Plan 06-04)
1. **Keyboard-only flow.** Walk these steps:
   1. On the home page, press Tab once and assert the skip link has focus.
   2. Press Enter and assert focus is on `main`.
   3. Press Ctrl+K, type a lesson ID, press Enter, and assert `h1#title` has focus.
   4. Tab into the editor and type. Then press Escape and Tab, and assert focus left `.cm-editor`.
   5. Press Ctrl+S and assert the `#save-state` text.
   6. Press Ctrl+Enter and wait for `#job-status`.
   7. Reach Saved runs with the keyboard and open the oldest entry.
   8. Assert there were no execution requests and the pad SHA-256 is unchanged.
2. **Focus visibility walk.**
   - Tab through up to 80 stops on a ready Python lesson and on a module reading lesson.
   - Every `document.activeElement` must show at least one of these:
     - a computed `outline-style` other than `none`, at least 2px wide
     - a `box-shadow`
     - a place in an explicit allowlist that names the replacement cue
   - Record the list in the report.
3. **axe scan,** only if the human approves the fetch.
   - Inject it with `page.add_script_tag(path="/axe/axe.min.js")`.
   - Run `axe.run(document, {runOnly: {type: "tag", values: ["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]}})`.
   - Scan these pages in both light and dark: the home page, a Python lesson, a SQL lesson, a module reading lesson, the DAX draft, a not-ready worker lesson, a browser lesson and the open palette.
   - Fail on `serious` or `critical` violations. Record `moderate` ones as an advisory list.
4. **Contrast table.** Add a node harness test that computes every pair in the table above. Assert 4.5:1 for text and 3:1 for focus cues.

## Q3. Learner State Audit

### Where state lives
| State | Store | Evidence |
|-------|-------|----------|
| Legacy pad source | `.learning/pads`, with content-addressed history in `history/practice-<sha>.ext`. That code never prunes it. | execution.py:455-510 |
| Legacy phase notes | `lab("save", {phase, note})`, once per phase | classroom.js:667-682 (`saveLesson`) |
| Module draft (source, prediction, explanation, review) | One slot per lesson in `.learning/modules/sessions.json`, with no history | modules.py:360-437 |
| Legacy run receipts | Append-only `.learning/classroom-runs/<lesson>/<language>/<mode>/<UTCstamp>_<id>.json`, validated on read | classroom.py:129-131, classroom_runs.py:240-277 and 325-346 |
| Module jobs | `.learning/modules/jobs/*.json`, the 30 newest per lesson | module_jobs.py:621-632 |
| Browser observations | BrowserRunStore, limit 20 | browser_runs.py:17-40 |
| Progress | `.learning/progress.json` | progress.py |
| Browser backup | localStorage `ds60.classroom.unsaved.<key>`, with the older fallback `ds60.module.unsaved.<id>` | classroom.js:620-627 and 1315-1318 |
| UI preferences | localStorage `ds60.classroom.*`: lastLesson, lastTrack, exercises, split, sidebarHidden, code-size, editor-height, tour-seen | classroom.js:554-616 |

### Transitions
| Transition | Behavior | Verdict |
|------------|----------|---------|
| Lesson switch, Home, palette | `openLesson` and `showHome` flush the save queue. They refuse to leave while the draft revision is newer than the saved one (classroom.js:916-930). | Safe |
| Browser Back and Forward | `popstate` flushes, then restores the route (classroom.js:4200-4222) | Safe |
| Tab close or reload | `beforeunload` calls `stashDraft(workspaceKey(), values())` and prompts when `saveTimer`, `pendingSaves` or an unsaved revision exists (classroom.js:4110-4120) | Safe, but see S1 for what happens on restore |
| Viewing an old legacy receipt | `classroom-history` and `classroom-run-result` are read-only (classroom.py:142-165). `openRunReceipt` (classroom.js:3183) fetches `classroom-run-result`, and `showLegacyResult` (3077) calls `resetResult()` and then renders. | No re-execution |
| Viewing an old module job | A click in `renderHistory` only calls `showJob(job)`. For a browser observation, it first stops the live preview (classroom.js:1606-1612). | No re-execution. No harness test covers this (gap T1). |
| Interrupted job | `ModuleJobs.get` asks the worker for status, or marks the job failed with "Source was retained and was not replayed" (module_jobs.py:539-592). Recovery needs a typed confirmation and never replays (594-619). The constructor only polls (184). `start()` is idempotent per `request_id` (341-375). | Safe |
| Runtime readiness refresh | Re-checks capability without touching the source (harness test at check_classroom_ui.mjs:1428) | Safe |
| Test setup: SQL reset | `prepare-sql` requires `"RESET TRAINING"`, takes the execution lock, and runs only `SqlRunner.setup()` and `verify()` [VERIFIED: lab.py:163-184]. The shell copy promises that saved code, notes and run history are kept (classroom-shell.js:625-665). | Safe for files. The gate should prove it with `learner_snapshot` before and after. |
| Classroom server restart | The token changes, so every request gets a 403 and the message `"The classroom restarted after this page opened. Reload the page to reconnect; work saved in the classroom is kept."` [VERIFIED: classroom.js:642-645]. A failed save stashes a backup (classroom.js:712-721). | Safe until reload, then see S1 |
| Explicit replace (starter, load from pad history, Try example, Use solution) | Each asks for confirmation, flushes first and stays undoable (classroom.js:1928-1960, 2511-2600 and 3828-3880). `runSolution` never changes the source and uses purpose `solution`. | Intended, not a violation |

### Re-execution audit result
No path re-executes code when the learner views history. [VERIFIED: files above]
- The history views call only read endpoints.
- The server never replays on recovery.
- The gate already asserts that receipt views send no `run` or `step-through` requests (check_classroom_browser.py:297-301).

### Draft-loss risk
- **S1 (high): A stale browser backup silently overrides a newer server draft.**
  - How the restore works: when a lesson opens and a backup exists with string `source`, `prediction` and `explanation` fields, the code writes the backup into the fields unconditionally. It then sets `savedRevisions` one behind, so the next flush saves the backup [VERIFIED: classroom.js:1313-1342].
  - The stash holds only the field values (`localStorage.setItem("ds60.classroom.unsaved." + key, JSON.stringify(fields))`, classroom.js:622). It has no base fingerprint and no timestamp.
  - Example of the loss:
    1. A save fails during a restart, so a backup is kept.
    2. The learner reloads in another tab, or comes back later, and saves newer work.
    3. The first tab then reopens the lesson.
    4. The old backup wins, and the next autosave overwrites the server slot.
  - Impact: for module lessons there is only one slot (modules.py:360-437). The newer draft is gone unless a job receipt happens to hold its source. Legacy pads can be recovered from pad history (execution.py:462-510).
- **S2 (low): A backup is cleared only when the same view saves the same fields** (classroom.js:697-707). An abandoned stash for a lesson the learner never reopens stays forever. That is harmless in itself, but it makes S1 more likely much later.
- **S3 (observation): `classroom_runs.history()` fails closed if one of the newest receipts is corrupt** (classroom_runs.py:325-346). This protects integrity, but it hides all history for that lesson. Leave it unchanged and document it. The UI already reports storage status.

## Architecture Patterns

### System Architecture Diagram
```
lesson payload (classroom-index / module-lesson / lab lesson)
        |
        v
  openLesson() --restore--> [backup check: stash.base == fingerprint(server fields)?]
        |                         | yes: restore silently (current behavior)
        |                         | no:  show choice panel, keep server draft until learner picks
        v
  workspaceMode(lesson, capability)  (pure, tested)
        |
        +--> capability strip: lesson kind | what Run does | where results appear | readiness
        +--> Run button label, disabled reason (aria-describedby)
        +--> results panel visibility + empty-result copy
        v
  Run --> worker / browser sandbox / psql / none --> receipt or job (append-only)
                                                        |
  Saved runs list --click--> showJob / showLegacyResult (read-only) --> "Saved run from <time>. Nothing ran again."
```

### Pattern 1: Pure mode descriptor
**What:** One function maps the payload to every piece of mode copy. `showCapability` and `resetResult` read from it instead of branching inline.

**Where:** In classroom.js, inside a new marked block, `// BEGIN WORKSPACE MODE PURE HELPERS` through `// END WORKSPACE MODE PURE HELPERS`. A pytest can then evaluate it with the pattern in tests/test_learning_editor.py:17-43.
```javascript
// Inputs come from fields already in the payload; no server change.
function workspaceMode(lesson, cap) {
  const profile = (cap && cap.profile) || lesson.runtime_profile || lesson.language;
  if (lesson.execution_mode === "draft")
    return { kind: "draft", run: null, results: "offline", ready: true,
             empty: "", where: "Comparison below the editor" };
  if (profile === "reading")
    return { kind: "reading", run: null, results: "none", ready: true,
             empty: "", where: "Your worksheet is saved with this lesson" };
  if (["javascript-browser", "html-browser"].includes(profile))
    return { kind: "browser", run: "Run browser preview", results: "preview",
             ready: !!cap.ready, where: "Preview frame in this browser tab",
             empty: "No preview yet. Press Run browser preview." };
  // legacy save-only and not-ready worker branches follow the same shape
  return { kind: "worker", run: "Run code", results: "console", ready: !!cap.ready,
           where: "Result panel", empty: "No run yet. Press Run code to try this lesson." };
}
```
The kind names and copy above are illustrative [ASSUMED]. The only payload values the function relies on are `execution_mode === "draft"`, `runtime_profile === "reading"`, `"javascript-browser"` and `"html-browser"` [VERIFIED: classroom.js:1502-1503 and 1516].

### Pattern 2: Fingerprinted backup
**What:** Store `{fields, base_sha256, saved_at}` instead of the bare fields. Compute `base_sha256` with `crypto.subtle.digest("SHA-256", ...)` over the stable JSON of the server fields loaded when the lesson opened. This assumes 127.0.0.1 counts as a secure context [ASSUMED].

**On reopen:**
- **Base matches:** restore the stash as the code does today.
- **Base differs, or an older stash has no base:** keep the server draft in the editor and show an inline panel built with `node()`: "A browser copy from <time> differs from your saved draft", with "Keep saved draft" and "Use browser copy". The second button goes through the existing confirm-and-flush replace path, so CodeMirror undo still works. Never auto-save until the learner chooses.

### Anti-Patterns to Avoid
- **Copy keyed on `current.engine` alone.** This is the cause of G2. Key on the descriptor instead.
- **Hiding `#runtime-results` with CSS only.** Use the `hidden` attribute so the gate's visibility checks and the accessibility tree agree.
- **Adding a fourth global keydown listener.** Extend the existing ones (classroom.js:3682 and 4100, classroom-shell.js:297) to avoid ordering bugs.
- **Calling any run endpoint to "refresh" an old result.**

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| WCAG rule scanning | Custom ARIA validators | axe-core in the gate | It maintains hundreds of rules |
| Modal focus trap | Another manual Tab trap | The `inert` attribute, or native `<dialog>.showModal()` | The palette already proves the native path |
| Leaving the editor with Tab | Custom Tab handling | CodeMirror's Escape then Tab, and the Ctrl-m toggle | Built in and documented upstream |
| Hashing | String hash functions | `crypto.subtle.digest` | Avoids collisions and edge cases |
| Contrast math | A new formula | The existing helpers in check_classroom_ui.mjs:1484-1725 and check_classroom_browser.py | Already sRGB-linearized and tested |

## Common Pitfalls

### Pitfall 1: Copy changes break exact-string tests
**What goes wrong:** The harness asserts `"The go runtime is not ready. Prepare this optional runtime with the module launcher first."` (check_classroom_ui.mjs:2467), and html:652 duplicates the "Press Run code" copy.

**How to avoid:** Keep the not-ready sentence prefix unchanged, update html:652 together with `resetResult`, and grep both scripts before committing any copy change.

### Pitfall 2: Gate selectors and the chooser baseline
**What goes wrong:** `tests/test_classroom_browser_probe.py:32` checks that the chooser baseline matches the current catalog sources, and other agents are editing `courses/*`.

**How to avoid:** Pick gate lessons by `runtime_profile` from `classroom-index` at run time by extending `choose_lesson` (check_classroom_browser.py:203-225). Do not add hardcoded IDs to the baseline.

### Pitfall 3: Running the gate against the wrong project
**How to avoid:** Always run `~/.cache/ds60sqlpy/run-browser.sh ds60-phase1-browser work/phase6-browser-receipts.json`. The checker refuses to run without `--confirm-disposable` (check_classroom_browser.py:1026). Never pass `ds60-classroom`.

### Pitfall 4: Native dialogs hang Playwright
**How to avoid:** Register `page.on("dialog", ...)` in any check that triggers a confirm or prompt (see K7).

### Pitfall 5: `inert` and the tour's own controls
**What goes wrong:** If the tour card is a descendant of `#main`, setting `inert` on `#main` disables the card too.

**How to avoid:** Mount the card outside the inert containers, or switch it to a `<dialog>`.

### Pitfall 6: Dashes in copy
**How to avoid:** Add a harness or pytest assertion that the changed assets and the new RESEARCH, PLAN and SUMMARY files contain no U+2013 or U+2014.

### Pitfall 7: The fake DOM lacks APIs
**What goes wrong:** The vm harness (check_classroom_ui.mjs:90-210) may not expose `crypto.subtle` or `inert`.

**How to avoid:** Inject `globalThis.crypto` from Node into the context. In the harness, assert that the `inert` attribute is set, and prove its behavior in the browser gate.

## Code Examples

### Read-only history click (current, keep)
```javascript
// Source: src/ds60sqlpy/assets/classroom.js:1606-1612
button.addEventListener("click", () => {
  if (job.kind === "browser_observation") {
    stopBrowserPreview("Stopped before viewing a saved observation.");
    updateControls();
  }
  showJob(job);
});
```

### Gate preservation idiom (existing helpers)
```python
# Source: scripts/check_classroom_browser.py:250-301 (learner_snapshot, assert_learning_state_unchanged, assert_no_execution_requests)
before = learner_snapshot(page, lesson)
requests = []  # collected by the existing request listener
open_oldest_saved_run(page)            # new helper, keyboard only
assert_no_execution_requests(requests)
assert_learning_state_unchanged(before, learner_snapshot(page, lesson))
audit.preserved(name, before_sha, after_sha)  # Audit, lines 100-128
```

### axe injection in the container [ASSUMED API usage]
```python
page.add_script_tag(path="/axe/axe.min.js")
result = page.evaluate("""() => axe.run(document, {runOnly: {type: 'tag',
  values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})""")
serious = [v for v in result["violations"] if v["impact"] in ("serious", "critical")]
```

The runner (outside the repo) needs one more read-only mount, `-v "$HOME/.cache/ds60sqlpy/axe/package":/axe:ro`, and the checker should accept `--axe-script PATH` and record `axe: skipped` when the path is absent, so the gate still runs without it.

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| A manual Tab trap plus `aria-modal` | `inert` on the background, or native `showModal()` | Real modality for assistive tech and for the mouse |
| `outline: none` on custom fields | `:focus-within` on the wrapper | Visible focus without double rings |
| An unversioned crash stash | A stash that carries a base fingerprint and a time | Conflicts are detected instead of the last writer winning |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | axe-core 4.14.1 is the legitimate Deque package and is safe to cache | Stack, Audit | Supply chain. Mitigated by the human checkpoint and the read-only mount. |
| A2 | `page.add_script_tag(path=...)` injects inline content, which the classroom CSP allows (`'unsafe-inline'` was observed) | Code Examples | If it is blocked, use `page.evaluate(source)` instead |
| A3 | `crypto.subtle` is available on `http://127.0.0.1` | Pattern 2 | If not, store a copy of the base fields and compare them directly |
| A4 | The descriptor's kind names and copy are illustrative | Pattern 1 | None. The planner chooses the final copy. |
| A5 | CodeMirror's macOS Ctrl-k binding deletes to the end of the line. The bundle shows a `Ctrl-k` binding, but the function name is minified. | K3 | Low. The fix is correct either way. |
| A6 | Native `confirm` and `prompt` dialogs are acceptable for UX-02 | K7 | If the UAT disagrees, a later phase replaces them |

## Open Questions

1. **Should module drafts keep a short history, for example the last 5 saves?**
   - What we know: module drafts use a single slot (modules.py:360-437), while legacy pads keep content-addressed history.
   - Recommendation: defer it. The S1 fingerprint fix removes the known loss path without a schema change.
2. **Should the mode strip also appear as a cue in the lesson list?** Recommendation: no. It is outside UX-01's scope.
3. **The Phase 1 human UAT on first-time clarity is still pending.** Recommendation: fold it into the Plan 06-04 human checkpoint and run it against the new mode strip.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | Gate | yes | 29.9.3 | none |
| Playwright image | Gate | yes | `mcr.microsoft.com/playwright/python:v1.64.1-noble` | none |
| `~/.cache/ds60sqlpy/linux-pw`, `run-browser.sh`, `forward.py` | Gate | yes | playwright 1.64.1 | none |
| Disposable stack `ds60-phase1-browser` | Gate | yes: lab, postgres and python-core-worker, on port 55015 | n/a | Recreate a disposable project. Never use ds60-classroom. |
| Node | UI harness | yes | v26.13.0 | pytest skips the harness when node is missing |
| `.venv/bin/python` and pytest | Tests | yes | pytest 9.1.1 (from pycache tags) | n/a |
| axe-core cache | The axe check in Plan 06-04 | no | n/a | Skip axe and keep the custom checks |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 with xdist, the node vm harness, and Playwright 1.64.1 in a container |
| Config file | pyproject.toml and Makefile:53-57 |
| Quick run command | `node scripts/check_classroom_ui.mjs src/ds60sqlpy/assets/classroom.js && .venv/bin/python -m pytest -q tests/test_module_ui.py tests/test_learning_editor.py tests/test_workspace_mode.py -n 0` |
| Full suite command | `make test` (Phase 1 baseline: 5694 passed) |
| Gate command | `~/.cache/ds60sqlpy/run-browser.sh ds60-phase1-browser work/phase6-browser-receipts.json` (Phase 1 baseline: 20/20 checks in Chromium at 1440x1000) |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UX-01 | The descriptor returns the correct run label, results kind and copy for each mode. Use 12 fixtures, including a GPU not-ready lesson and a legacy save-only lesson. | unit (vm) | `pytest tests/test_workspace_mode.py -n 0` | no, Wave 0 |
| UX-01 | Reading lessons hide `#runtime-results` and never say "Press Run code". The browser empty copy matches the button. | harness | `node scripts/check_classroom_ui.mjs ...` | extend |
| UX-01 | An old module job shows "Saved run from" and a note that nothing reran | harness | same | extend |
| UX-01 | The mode strip is visible and correct on one sampled lesson per mode | gate | run-browser.sh | extend |
| UX-02 | The tour sets and clears `inert`. The palette shows a focus cue. On macOS, Ctrl+K in the editor does not open the palette. `#run` is described by `#capability`. | harness | node harness | extend |
| UX-02 | The token contrast table holds: text at 4.5:1, focus cues at 3:1 | harness | node harness | extend |
| UX-02 | The keyboard-only flow, the focus visibility walk and axe (if approved) all pass | gate | run-browser.sh | extend |
| STATE-01 | A stale backup with a different base shows a choice and does not autosave. A backup with a matching base restores. | harness | node harness | extend |
| STATE-01 | A click in the module Saved runs list never calls `module-run` or `module-step` (gap T1) | harness | node harness | extend |
| STATE-01 | Preservation receipts cover lesson switch, Back, viewing an old receipt, SQL reset, readiness refresh and reload | gate | run-browser.sh, report section `preservation` | extend |

### Sampling Rate
- **Per task commit:** the quick run command.
- **Per wave merge:** `make test` plus the node harness.
- **Phase gate:** the full suite is green and the gate report shows `complete: true` with every check passed. Then run `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_workspace_mode.py`. Reuse the evaluate pattern from tests/test_learning_editor.py:17-43 with the new markers.
- [ ] Harness context. Inject `crypto` into the vm sandbox (check_classroom_ui.mjs:90-210).
- [ ] Gate. Add the `--axe-script` option and a `page.on("dialog")` helper.

## Security Domain

### Applicable ASVS Categories (Level 1)
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | The per-start token is unchanged (classroom_http.py:216-225) |
| V3 Session Management | no | Rotating the token on restart is intentional. Keep the 403 copy. |
| V4 Access Control | yes, unchanged | Host, Origin and token checks (tests/test_unified_classroom.py:148-215) |
| V5 Input Validation | yes | Validate the shape of the parsed stash (strings only, bounded length) before using it. Add no new server fields. |
| V6 Cryptography | minimal | Web Crypto SHA-256 for fingerprints only. No secrets involved. |
| V14 Output Encoding | yes | Render times, profile names and copy with `textContent` and `node()` only |

### Known Threat Patterns
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A tampered localStorage stash injects markup | Tampering | Render with `textContent`, never `innerHTML` |
| A third-party script (axe) in the gate | Tampering | Pinned version, human checkpoint, read-only mount. It is test-only and the classroom never serves it. |
| The gate touches learner data | Information disclosure | Run only with `--confirm-disposable` against `ds60-phase1-browser` |

## Recommended Plans

Within each wave, the plans touch different files, which avoids merge conflicts.

| Wave | Plan | Req | Files | Verification |
|------|------|-----|-------|--------------|
| 1 | **06-01 Workspace mode descriptor** | UX-01 | classroom.js (descriptor block, showCapability, resetResult, renderLegacyControls, and the showJob title and note); classroom.html (mode strip near html:180, `aria-describedby` on `#run`, the html:652 copy); classroom.css (strip styles); new tests/test_workspace_mode.py; check_classroom_ui.mjs | Unit fixtures for 12 modes. Harness tests for reading, browser, save-only and old module jobs. No exact-string regressions. |
| 2 | **06-02 Draft backup fingerprint and history safety** | STATE-01 | classroom.js (stashDraft, queueSave, beforeunload, the openLesson restore, and a choice panel built with `node()`); check_classroom_ui.mjs | A stale-backup choice test. A matching-backup restore test. A module history click makes no run call (T1). The storage-unavailable path is unchanged (test at line 1446). |
| 2 | **06-03 Keyboard and focus fixes** | UX-02 | classroom-guide.js (inert); classroom-shell.js (macOS K); classroom.css (palette focus-within, manual-parts border); the classroom.html manual keys table (add Ctrl M and Shift Alt M); new scripts/check_classroom_keyboard.mjs and tests/test_classroom_keyboard.py | Harness tests for K1 to K5 and the token contrast table. It makes no edits to classroom.js, so it can run in parallel with 06-02. |
| 3 | **06-04 Desktop gate extension and UAT** | all | scripts/check_classroom_browser.py; tests/test_classroom_browser_probe.py (offline unit tests for the new helpers); the external run-browser.sh mount | A checkpoint:human-verify before the axe fetch. A gate report at work/phase6-browser-receipts.json covering: the mode sample (Python, SQL snippet and whole lesson, module ready, module not ready, reading, DAX, browser), the keyboard flow, the focus walk, axe, and preservation receipts. A checkpoint:human-verify for the Phase 1 clarity UAT on the new strip. |

**Risks:** copy changes can break string asserts (Pitfall 1); concurrent agents can change the catalog (Pitfall 2); 06-01 and 06-02 both touch classroom.js, so they must stay in different waves; the focus walk may flag CodeMirror internals (allowlist `.cm-content`, because `.code-editor:focus-within` draws the ring); axe moderate findings on vendor markup are advisory, never fixed in vendored code.

## Sources

### Primary (HIGH confidence)
- **Repo source read this session:** the UI assets (classroom.js, classroom-shell.js, classroom-editor.js, classroom-guide.js, classroom.css, classroom.html, entry.mjs), the server modules (classroom.py, classroom_http.py, classroom_runs.py, module_service.py, module_jobs.py, modules.py, execution.py, capabilities.py, curriculum_framework.py, browser_runs.py, module_drafts.py, lab.py:160-185), and the tests and tooling (check_classroom_ui.mjs, check_classroom_browser.py, tests/test_learning_editor.py, tests/test_module_ui.py, tests/test_unified_classroom.py, Makefile, run-browser.sh).
- **Live disposable stack:** the `classroom-index` census and the CSP header, both read with curl (read-only).

### Secondary (MEDIUM confidence)
- codemirror.net/examples/tab: Escape then Tab, and the Ctrl-m toggleTabFocusMode binding.
- `npm view axe-core`: version 4.14.1, MPL-2.0, dequelabs repository.

### Tertiary (LOW confidence)
- The axe tag set and the Playwright injection API (training knowledge, flagged as A1 and A2).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH for the existing tools. MEDIUM for axe, because the SUS verdict came from a lookup gap.
- Architecture: HIGH. Every recommendation hooks into an existing function at a cited line.
- Pitfalls: HIGH. Each one is backed by a file reference.

**Research date:** 2026-11-18
**Valid until:** 2026-12-18 for code references. Re-run the catalog census before Plan 06-04, because `courses/*` is changing.
