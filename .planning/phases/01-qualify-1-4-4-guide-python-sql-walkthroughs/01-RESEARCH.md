# Phase 1: Qualify 1.4.4 Guide and Python/SQL Walkthroughs - Research

**Researched:** 2026-11-23
**Domain:** Desktop classroom documentation, guided walkthrough UI, Python tracing, SQL planning and PostgreSQL execution
**Confidence:** MEDIUM

## User Constraints

### Locked Decisions (verbatim from `.planning/STATE.md`)

- “Phase 1 qualifies the unfinished 1.4.4 checkpoint; it does not claim that the broader overhaul is complete or published.”
- “All existing language and subject tracks are in scope. Python and SQL are a quality reference and checkpoint, not a scope boundary.”
- “Preserve desktop-only delivery, local Docker and trusted-local-code boundaries, stable lesson IDs, learner state, and capability distinctions.”
- “Keep runtime builds, image scans, registry publication, and cleanup as separately verified gates.”
- “Verify the Docker Hub target immediately before any publication; do not stop unrelated containers or remove learner volumes.”

[VERIFIED: `.planning/STATE.md:51-54,63`]

### Scope and execution constraints

- The active checkpoint is Phase 1 and covers GUIDE-01, GUIDE-02, WALK-01, WALK-02, and WALK-04. Qualification must not imply that the broader overhaul is complete or published. [VERIFIED: `.planning/ROADMAP.md:24-31`]
- Research only. Modify only this research file. Do not modify application code, run builds, start or stop containers, change other planning artifacts, push, or publish. Preserve learner data and do not assume a Docker Hub target. [VERIFIED: user-provided phase instructions]
- No phase `CONTEXT.md` was present in the initialized phase context; there are no additional CONTEXT decisions to copy. [VERIFIED: GSD phase initialization]

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GUIDE-01 | A learner can open the classroom guide from the home screen and lesson workspace, find what each major screen and control does, and follow initialization and lesson-switching instructions. | Verify manual content and both entry routes. Correct or qualify the unverified Hub command; use the desktop browser acceptance route. |
| GUIDE-02 | A learner can start, dismiss, and restart the optional classroom tour without changing the selected lesson, overwriting work, or starting code execution. | Add browser-level lifecycle checks that preserve lesson selection and draft and assert that no run or walkthrough request occurs. Cover the no-selection home route separately. |
| WALK-01 | A Python walkthrough presents a bounded, testable execution trace with relevant source location, event, stack or local state, output, and clear limit or error behavior. | Reuse the current bounded trace worker; add focused tests for source links, events, state, limits, and error behavior. |
| WALK-02 | A SQL walkthrough explains only its documented, verified query subset, ties clause highlights to source offsets and PostgreSQL results, and clearly handles unsupported input without modifying learner data. | Derive the documented subset from the existing planner, test offset mapping, and qualify supported and unsupported input against the disposable PostgreSQL 17 CI service. Account for course-database preparation before parsing. |
| WALK-04 | Learners can distinguish a code walkthrough from an ordinary run and inspect a solution walkthrough without replacing their own draft. | Verify the distinct `step-through` action and `practice`/`solution` purpose end to end; assert saved source and run history remain unchanged for Python and SQL. |
</phase_requirements>

## Summary

Keep the existing classroom architecture and add acceptance coverage around its current manual, tour, and walkthrough routes. The fast UI harness currently loads `classroom.js`, while tour and walkthrough behavior lives in `classroom-guide.js`; the actual browser checker is the appropriate place to verify user-visible lifecycle and draft-preservation behavior. The harness passed 94 checks during this research, but this does not qualify the tour or walkthrough flows. [VERIFIED: `scripts/check_classroom_ui.mjs:1-5`; `classroom-guide.js:1-235,550-800`; local run of `node scripts/check_classroom_ui.mjs`]

The backend already separates step-through from ordinary execution and documents that the walkthrough does not save a pad, write a receipt, or touch history. Python tracing has explicit bounds. SQL planning supplies statement and step offsets, but an internal planner fallback produces a whole-query step rather than an unsupported result. Further, SQL course preparation currently runs before the walkthrough parser. Tests and learner-facing claims must reflect those behaviors rather than promise that every unrecognized SQL construct is rejected or that a walkthrough has no database setup effects. [VERIFIED: `lab.py:357-360,393-404`; `step_through.py:18-30,1026-1059`]

**Primary recommendation:** Keep runtime dependencies unchanged. Fix the guide's unverified image-pull instruction, make the tour selection-neutral, and qualify trace/highlight behavior with focused unit tests, disposable PostgreSQL integration, and the existing desktop browser route.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Manual entry and routing | Browser / Client | - | Home/workspace links and the manual return route are client-side navigation. [VERIFIED: `classroom.html:945-1001`; `classroom.js:4159-4207`] |
| Tour state and lifecycle | Browser / Client | - | The tour overlay and its selection/navigation side effects are implemented in the classroom guide script. [VERIFIED: `classroom-guide.js:550-800`] |
| Walkthrough request and presentation | Browser / Client | API / Backend | The client snapshots source, sends a distinct lab action, and renders the returned trace; the lab validates and dispatches it. [VERIFIED: `classroom-guide.js:150-180`; `lab.py:345-410`] |
| Python trace execution | API / Backend | Browser / Client | The backend runs and bounds the trace; the client maps events to source and presents state/output. [VERIFIED: `step_through.py:18-30,839-848`; `classroom-guide.js:1-235`] |
| SQL clause execution and result | Database / Storage | API / Backend | The backend plans source spans and a restricted worker executes SQL against PostgreSQL; the client renders highlights and results. [VERIFIED: `step_through.py:609-664,1026-1059`] |
| Learner drafts, receipts, and history | API / Backend | Database / Storage | Ordinary run persistence is a separate path from the no-save walkthrough path. Preserve the existing storage contract. [VERIFIED: `lab.py:357-360`; `tests/test_learning_lab.py`] |

## Standard Stack

### Core

| Library / component | Version | Purpose | Why Standard |
|--------------------|---------|---------|--------------|
| Python runtime and standard library | Project range is `>=3.11,<3.13`; prepared environment is Python 3.12.16 | Execute bounded Python traces and backend tests | The project pins this runtime range and uses the existing trace worker; no tracing dependency is needed. Quote from `pyproject.toml`: `requires-python = ">=3.11,<3.13"`. [VERIFIED: `pyproject.toml:7-10`; local `.venv` probe] |
| Existing classroom JavaScript | No new package | Manual, tour, trace requests, and result presentation | Existing browser assets own these behaviors. Reuse them rather than add a second client implementation. [VERIFIED: `classroom.js`; `classroom-guide.js`] |
| PostgreSQL | 17 in the existing integration service | Verify SQL step results and data-state safety | The existing CI job provisions PostgreSQL 17; SQL subject guidance also sets PostgreSQL 17 as canonical automation. Quote from CI: `image: postgres:17`. [VERIFIED: `.github/workflows/ci.yml:225-266`; `sql/AGENTS.md:7-13`] |
| Pytest and pytest-xdist | Local `.venv`: pytest 9.1.1; xdist available | Focused unit and opt-in database integration tests | Existing tests and fixtures use pytest; parallel database tests require load-group distribution or serial execution. [VERIFIED: `tests/conftest.py:9-13,57-71`; local `.venv` probe] |

### Supporting

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| Node.js built-ins | Local Node 26.13.0 | Run the bounded, dependency-free classroom UI regression harness | Run after client changes; the harness imports `node:assert/strict`, `node:fs`, and `node:vm`. [VERIFIED: `scripts/check_classroom_ui.mjs:1-5`; local probe] |
| Playwright browser test environment | CI lock declares Playwright 1.64.1; package legitimacy verdict is SUS | Desktop Chromium acceptance | Use only the existing isolated browser/CI environment after the required human verification checkpoint; do not add it to application runtime. [VERIFIED: `requirements/ci-browser.lock:6-13`, package-legitimacy check; WARNING below] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Existing Python trace and SQL planner | A new tracing or SQL parser package | Do not introduce a second execution model or parser for this checkpoint. The current backend already returns bounded traces and source spans; qualify its supported behavior. [VERIFIED: `step_through.py:18-30,1026-1059`] |
| Existing browser acceptance script | A new browser automation framework | Extend `scripts/check_classroom_browser.py` so the phase uses the repository's existing browser route and disposable-state warning. [VERIFIED: `scripts/check_classroom_browser.py`; `docs/validation.md:433-448`] |

**Installation:** No new application packages are required. The browser packages below are already in a test-only hashed lock, not the application runtime. Do not install them locally until the SUS verdict has been reviewed.

**Version verification:** The project Python range, prepared Python version, PostgreSQL 17 CI image, and browser lock pins were read from source or probed this session. No application package upgrade is recommended. The registry check found the test package names, but the package-legitimacy verdict is SUS, so registry presence alone is not approval.

## Package Legitimacy Audit

This phase does not propose new runtime dependencies. The existing browser test lock declares, verbatim, `playwright==1.64.1`, `pyee==14.0.0`, `greenlet==3.5.6`, and `typing_extensions==4.16.0`. [VERIFIED: `requirements/ci-browser.lock:6-13`]

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `playwright` 1.64.1 | PyPI | Not established for this pinned release | Not returned | Not established by the legitimacy result | SUS | Existing CI-only pin. [WARNING: flagged as suspicious - verify before using.] Human verification checkpoint before any new install. |
| `pyee` 14.0.0 | PyPI | Not established for this pinned release | Not returned | Not established by the legitimacy result | SUS | Existing CI-only transitive pin. [WARNING: flagged as suspicious - verify before using.] Human verification checkpoint before any new install. |
| `greenlet` 3.5.6 | PyPI | Not established for this pinned release | Not returned | Not established by the legitimacy result | SUS | Existing CI-only transitive pin. [WARNING: flagged as suspicious - verify before using.] Human verification checkpoint before any new install. |
| `typing_extensions` 4.16.0 | PyPI | Not established for this pinned release | Not returned | Not established by the legitimacy result | SUS | Existing CI-only transitive pin. [WARNING: flagged as suspicious - verify before using.] Human verification checkpoint before any new install. |

The package-legitimacy seam returned SUS for all four names. The pinned versions were checked against PyPI; no install occurred. Do not treat registry existence as proof of legitimacy. [VERIFIED: GSD package-legitimacy and PyPI registry checks]

**Packages removed due to SLOP verdict:** none.
**Packages flagged as suspicious SUS:** `playwright`, `pyee`, `greenlet`, `typing_extensions`. Planner must add a `checkpoint:human-verify` before any install not already supplied by a reviewed CI environment.

## Project Constraints (from AGENTS.md and subject guidance)

- The classroom is desktop-only and local-Docker oriented. Preserve trusted-local-code boundaries, lesson identity, drafts, progress, and receipts; do not describe the execution environment as a security sandbox. [VERIFIED: `AGENTS.md:5-18,108-126`]
- Lead learner instructions with the Docker classroom. Use the prepared contributor environment for host commands; target Python 3.11-3.12 and use Python 3.12 for canonical examples and CI. [VERIFIED: `python/AGENTS.md:5-15`]
- SQL guidance targets PostgreSQL 16 or newer, with PostgreSQL 17 canonical automation. Use the disposable `advanced_sql_training` database and `training` schema; run SQL files with `psql -X -v ON_ERROR_STOP=1`. Do not run destructive reset/DDL against shared or learner data. [VERIFIED: `sql/AGENTS.md:5-25`]
- Keep capability distinctions explicit. A Python trace is not a general debugger; the SQL walkthrough covers only the parser's verified subset. Do not present other SQL dialects as runnable PostgreSQL. [VERIFIED: `.planning/REQUIREMENTS.md:11-22`; `sql/AGENTS.md:18`]
- No `copilot-instructions.md` directives were available in the project context. No additional project-specific constraints from that file are included.

## Architecture Patterns

### System Architecture Diagram

```text
Home screen / lesson workspace
        |
        +--> Manual link --> manual view --> return to previous classroom route
        |
        +--> Optional tour --> client overlay --> dismiss / restart / complete
        |                         |
        |                         +--> must not change lesson, draft, or execute code
        |
        +--> Walkthrough button + source snapshot
                  |
                  +--> lab action: step-through
                           |
                           +--> Python --> bounded trace worker
                           |                 --> source-linked events/state/output
                           |
                           +--> SQL --> statement selection and clause planner
                                         --> restricted PostgreSQL worker
                                         --> row previews and source-offset highlights
                  |
                  +--> client renders result without replacing the editor draft

Ordinary Run --> separate execution/persistence path --> draft/receipt/history
```

The diagram reflects the existing separation between the guide client, lab dispatch, trace worker, SQL worker, and ordinary run path. It is not a proposal to move responsibilities between tiers. [VERIFIED: `classroom-guide.js:150-180`; `lab.py:345-410`; `step_through.py:609-664,839-848`]

### Recommended Project Structure

```text
src/ds60sqlpy/assets/
├── classroom.html          # guide/manual content and entry links
├── classroom.js            # classroom navigation and manual return
└── classroom-guide.js      # tour, walkthrough request, trace display
src/ds60sqlpy/
├── lab.py                  # action validation and dispatch
├── execution.py            # execution worker and SQL worker boundary
└── step_through.py         # bounded Python trace and SQL plan/highlights
tests/
├── test_learning_lab.py    # saved-pad and action behavior
└── test_execution.py       # worker and PostgreSQL integration behavior
scripts/
├── check_classroom_ui.mjs
└── check_classroom_browser.py
```

These are existing source locations; prefer focused additions to their current tests and checker rather than inventing a parallel subsystem. [VERIFIED: repository files read this session]

### Pattern 1: Source snapshot walkthrough

**What:** The client sends the current source text and a `purpose`; the lab routes a distinct action to the trace worker. Walkthrough output is separate from ordinary run persistence.
**When to use:** Python or SQL walkthrough, including inspection of a solution.
**Example from client:** the exact purpose mapping is `purpose: purpose === "solution" ? "solution" : "practice"` and the request is `lab("step-through", fields, false)`. [VERIFIED: `classroom-guide.js:150-180`]

**Backend contract, verbatim:** “Trace a pad without saving it, writing a receipt or touching its history.” The accepted purpose values are `{"practice", "solution"}`. [VERIFIED: `lab.py:357-385`]

### Pattern 2: Bound and report trace events

**What:** Keep limits in the existing trace worker and return the event/state/output fields as data; use the frontend to map returned source locations to visible code.
**When to use:** Every Python walkthrough and any SQL step display.
**Limits quoted verbatim from the source:** `MAX_STEPS = 400`; `OUTPUT_CAP = 65_536`; `RESULT_FILE_CAP = 2_000_000`; `VALUE_LIMIT = 120`; `MAX_VARIABLES = 40`; `MAX_FRAMES = 8`; `PREVIEW_ROWS = 20`; `MAX_SQL_STEPS = 40`; `SQL_CELL_LIMIT = 1_000`; `SQL_LINE_CAP = 262_144`. [VERIFIED: `step_through.py:18-30`]

Python event classification is constrained by this source line: `"event": event if event in {"line", "call", "return", "exception"} else "line"`. [VERIFIED: `step_through.py:839-848`]

### Pattern 3: Tie SQL explanation to parser offsets and database results

**What:** Use the planner's statement and step offsets to render highlights; execute accepted steps through the existing restricted worker and compare results on PostgreSQL 17.
**When to use:** Documenting or changing the SQL walkthrough subset.
**Important:** A thrown internal `_Fallback` creates a whole-query step. It does not mean the input was rejected. Quote from source: `except _Fallback:` followed by `steps, unsupported = [_whole_step(statement)], None`. [VERIFIED: `step_through.py:1053-1059`]

For explicitly rejected or empty plans, the execution layer returns an empty step list and an `unsupported` result. The exact JSON uses `"kind": "sql"`, `"steps": []`, and `"elapsed_seconds": 0.0`. [VERIFIED: `execution.py:762-772`]

### Anti-Patterns to Avoid

- Do not describe the existing parser as a complete PostgreSQL parser. Treat its code and PostgreSQL integration results as the support boundary. [VERIFIED: `step_through.py:1022-1059`]
- Do not implement tour navigation by switching the selected lesson just to obtain a tour context. The current home/manual route has a branch that selects the Python track or first available track; explicitly test and correct this path. [VERIFIED: `classroom-guide.js:758-771`]
- Do not render learner code, SQL results, or errors as trusted HTML. Preserve safe text rendering in the guide. [VERIFIED: `classroom-guide.js` rendering helpers]
- Do not conflate ordinary Run and step-through requests, or hydrate the editor with solution source when a learner chooses to inspect a solution. [VERIFIED: `classroom-guide.js:150-180`; `tests/test_learning_lab.py`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Python event tracing, frame/local summaries, limits | A second tracer or custom serializer | Existing `step_through.py` trace worker | It already owns event capture, limits, output handling, and response fields. [VERIFIED: `step_through.py:18-30,839-848`] |
| SQL tokenization, planning, and offsets | A second SQL parser or guessed highlight spans | Existing `tokenize`, `plan_sql`, and `SqlPlan` | Source offsets and fallback behavior are already centralized. Add tests for the accepted subset instead. [VERIFIED: `step_through.py:1022-1059`] |
| Browser persistence and UI checks | A new harness that bypasses classroom routes | Existing `scripts/check_classroom_ui.mjs` and `scripts/check_classroom_browser.py` | The UI harness is fast; the browser checker exercises a real classroom with an explicit disposable-target confirmation. [VERIFIED: harness source; `docs/validation.md:433-448`] |
| PostgreSQL semantics | SQL mocks as the only evidence | Existing opt-in PostgreSQL fixture and PostgreSQL 17 CI service | Mocks cannot establish actual server behavior or the safety of the worker transaction. [VERIFIED: `tests/test_execution.py:450-475`; `.github/workflows/ci.yml:225-266`] |

**Key insight:** The phase is a qualification and test-coverage checkpoint, not a reason to add another execution stack. Make supported behavior explicit, preserve the current no-save boundary, and prove SQL behavior using the existing disposable database path.

## Common Pitfalls

### Pitfall 1: The home tour changes the active route

**What goes wrong:** Starting a tour from the home/manual path can select a track, violating selection preservation.
**Why it happens:** The current tour entry path resolves a missing lesson by choosing a track. Its fallback expression is `subjects.find((item) => item.id === "python") || subjects[0]`; the no-lesson path calls `switchTrack(subject.id)`. [VERIFIED: `classroom-guide.js:758-771`]
**How to avoid:** Test with a selected lesson, a draft, and an existing run counter; also test the no-selection home case. Start, dismiss, restart, and complete the tour while asserting that selection and draft remain unchanged and no run or walkthrough API request occurs.
**Warning signs:** URL/selected lesson changes, the editor receives a different pad, or a run counter increments. [VERIFIED: `classroom-guide.js:758-771`; tour lifecycle `:550-800`]

### Pitfall 2: Manual gives an unverified publication target

**What goes wrong:** The manual's image-pull command can be mistaken for an approved owner/tag. The same repository declares a different project version.
**Why it happens:** The manual contains `./classroom --all --from-hub sadatnfs --tag 1.4.4`, while the package metadata contains `version = "1.4.3"`. These strings do not verify a Docker Hub target.
**How to avoid:** Keep local `./classroom doctor` and `./classroom` guidance primary; verify the Hub owner and tag immediately before any publication or image-pull instruction is promoted. Do not publish or infer an owner in this phase.
**Warning signs:** Documentation treats the `1.4.4` tag or `sadatnfs` owner as authoritative without a fresh owner check. [VERIFIED: `classroom.html:956-961`; `pyproject.toml:7`]

### Pitfall 3: Unsupported SQL can still execute as a whole-query step

**What goes wrong:** A planner fallback may execute a query as one step rather than return `unsupported`; claiming that all unknown syntax is rejected is inaccurate.
**Why it happens:** The source catches `_Fallback` and sets a whole-query step with no unsupported message.
**How to avoid:** Document only cases confirmed by direct planner tests and PostgreSQL 17 integration. Make unsupported cases visible and safely handled; assert before/after state in a disposable database. Do not rely on read-only mode alone to make arbitrary SQL functions side-effect free.
**Warning signs:** Tests cover only the `unsupported` response branch and omit the `_Fallback` branch. [VERIFIED: `step_through.py:1053-1059`; PostgreSQL docs cited below]

### Pitfall 4: SQL setup may run before input is parsed

**What goes wrong:** A step-through request can prepare course database objects before invalid or unsupported SQL is rejected.
**Why it happens:** `LabServer._step_through` calls `ensure_before_run` before `PadRunner.step_through` parses the SQL.
**How to avoid:** Test against an already prepared disposable fixture and distinguish one-time course setup from query effects. Consider validating/planning before database preparation if the acceptance contract requires unsupported input to have no database changes.
**Warning signs:** A test starts with an empty database and attributes newly created course objects to the query, or ignores initialization side effects. [VERIFIED: `lab.py:393-404`; `sql_readiness.py:168-195`]

### Pitfall 5: Read-only SQL and repeat evaluation are not absolute side-effect guarantees

**What goes wrong:** PostgreSQL read-only transaction mode is not a promise that every invoked function or external effect is harmless; a step runner that executes an expression and then wraps it for counting may evaluate it more than once.
**Why it happens:** The SQL worker uses read-only transaction settings and result counting; PostgreSQL documents that read-only is a high-level restriction and does not prevent every kind of write.
**How to avoid:** Restrict learner-facing claims to verified, side-effect-safe query forms; use deterministic read-only examples and assert the database state before and after. Keep statement and lock timeouts and the existing limited-role checks.
**Warning signs:** Tests use volatile or extension functions, assume a SELECT has no side effects, or expect exact results from repeated nondeterministic expressions. [VERIFIED: `step_through.py:609-664`; CITED: PostgreSQL 17 transaction and hot-standby documentation]

### Pitfall 6: Browser acceptance mutates its target

**What goes wrong:** The browser checker creates test pads/progress and can pollute a learner classroom if pointed at it.
**Why it happens:** The checker intentionally tests persistence behavior.
**How to avoid:** Run only against an explicitly disposable classroom URL and pass `--confirm-disposable`; write its report under `work/`. Do not use cleanup that tears down shared Compose projects or volumes.
**Warning signs:** The URL points to a personal workspace or the cleanup target is not a uniquely owned disposable project. [VERIFIED: `docs/validation.md:433-448`; `scripts/check_classroom_browser.py:650-678`; `scripts/ci_classroom.py:458-463`]

## Code Examples

Verified patterns from the current source:

### Distinct walkthrough action

The client sends a separate action with an explicit purpose. The values in this example are quoted from the client source:

```javascript
const fields = {
  lesson_id: current.id,
  language,
  code,
  purpose: purpose === "solution" ? "solution" : "practice",
  timeout_seconds: Number(byId("timeout")?.value) || 60,
};
const result = await lab("step-through", fields, false);
```

The request/action values `"solution"`, `"practice"`, and `"step-through"` are verbatim from `classroom-guide.js:150-180`. The timeout fallback and request flag are verbatim `"timeout_seconds: Number(byId("timeout")?.value) || 60,"` and `lab("step-through", fields, false)`. Backend accepted purpose values are `{"practice", "solution"}`. [VERIFIED: `classroom-guide.js:150-180`; `lab.py:357-385`]

### SQL rejection response shape

The following response shape is quoted from the execution source; retain an explicit unsupported outcome rather than silently presenting an empty highlight. The source values include `"kind": "sql"`, `"steps": []`, `"elapsed_seconds": 0.0`, and `"error": None`:

```python
if plan.unsupported is not None or not plan.steps:
    return {
        "kind": "sql",
        "statement": plan.statement,
        "statement_offset": plan.statement_offset,
        "steps": [],
        "unsupported": plan.unsupported or stepping.NO_QUERY,
        "elapsed_seconds": 0.0,
        "error": None,
    }
```

This is the existing response branch. It does not cover the separate whole-query fallback branch in `plan_sql`. [VERIFIED: `execution.py:762-772`; `step_through.py:1053-1059`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Use the ordinary run path to inspect execution | Use the separate `step-through` action with a source snapshot and no-save contract | Already present in the current implementation; exact introduction date not established | Preserve this separation; acceptance must prove it does not replace drafts or add receipts/history. [VERIFIED: `lab.py:345-385`] |
| Treat SQL walkthrough support as all of PostgreSQL | Use the existing parser's documented subset, source offsets, and PostgreSQL 17 integration evidence | Current checkpoint | Do not describe unsupported syntax as supported merely because a whole-query fallback runs. [VERIFIED: `step_through.py:1022-1059`] |

**Deprecated/outdated:**
- Do not treat the manual's Hub owner/tag as a verified release target. It conflicts with the declared package version and must be revalidated before publication. [VERIFIED: `classroom.html:956-961`; `pyproject.toml:7`]

## Assumptions Log

No unverified package or release target is recommended. The Docker Hub owner/tag is an explicit verification checkpoint, not an assumption.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| N/A | None | N/A | N/A |

## Open Questions

1. **What exact SQL grammar will the guide promise?**
   - What we know: the planner recognizes query entry forms including `SELECT`, `WITH`, `VALUES`, and `TABLE`; an internal fallback may return a whole-query step. [VERIFIED: `step_through.py:1022-1059`]
   - What's unclear: which grammar cases are intended to be documented and which unsupported/fallback cases need a visible warning.
   - Recommendation: use targeted planner tests plus PostgreSQL 17 tests to define the smallest safe, useful subset; do not promise all PostgreSQL syntax.

2. **Should SQL syntax be validated before course database preparation?**
   - What we know: `ensure_before_run` currently occurs before `PadRunner.step_through`. [VERIFIED: `lab.py:393-404`]
   - What's unclear: whether acceptance allows course fixture setup as a side effect when a query is rejected.
   - Recommendation: decide explicitly in planning. For a strict no-change contract, parse/validate before preparation and include a before/after database-state test.

3. **Which Docker Hub owner and tag, if any, should the manual document?**
   - What we know: the current manual contains a concrete Hub command, while project metadata declares `1.4.3`; the phase decision requires a fresh target check before publication. [VERIFIED: `classroom.html:956-961`; `pyproject.toml:7`; `.planning/STATE.md:63`]
   - What's unclear: approved owner/tag and whether this manual should describe Hub pulls at all.
   - Recommendation: do not infer an answer. Keep local initialization guidance actionable and require owner confirmation before documenting or using a registry target.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Prepared Python environment | Focused backend tests | Yes | Python 3.12.16; pytest 9.1.1 | Use the repository's prepared `.venv`; system Python 3.14.6 is outside the declared project range. |
| Node.js | Fast UI regression | Yes | 26.13.0 | No install needed for the dependency-free harness. |
| Docker Engine and Compose | Disposable container-based qualification | Yes, but not started or changed | Engine 29.9.3; Compose 5.7.1 | Prefer existing CI disposable services; do not run local lifecycle commands for this research task. |
| PostgreSQL client/server | SQL integration | `psql` not found; no local disposable PostgreSQL service was established | CI uses PostgreSQL 17 | Run only in the existing PostgreSQL CI job or provision a separately approved disposable service. Never point tests at learner/shared data. |
| Playwright and Chromium | Real desktop-browser acceptance | Not available on this host | No Playwright Python module or Chromium executable found on PATH | Use a reviewed, isolated CI browser environment; require the package human-verification checkpoint before any new installation. |
| Disposable classroom URL | Browser persistence checks | Not established | N/A | Use only a newly provisioned disposable classroom. Do not substitute a learner URL. |

Local availability facts are from probes this session. The existing CI workflow defines a PostgreSQL 17 service, and `scripts/ci_classroom.py` provisions a separate browser environment from the hashed test lock. [VERIFIED: `.github/workflows/ci.yml:225-266`; `scripts/ci_classroom.py:343-355`]

**Missing dependencies with no fallback:**
- None for code-only research or fast UI tests. Real SQL/browser acceptance remains blocked until the dedicated disposable PostgreSQL and browser environments are available.

**Missing dependencies with fallback:**
- PostgreSQL local tooling: use the existing PostgreSQL 17 CI service.
- Playwright/Chromium: use the isolated CI browser environment after package review.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 in the prepared `.venv`; pytest-xdist is available |
| Config file | `pyproject.toml` and `tests/conftest.py` |
| Quick run command | `node scripts/check_classroom_ui.mjs` |
| Focused backend command | `env -u DS60_TEST_DATABASE_URL -u DS60_SQL_EXPANSION_TEST_URL -u DS60_DATABASE_URL .venv/bin/python -m pytest -n 0 tests/test_learning_lab.py tests/test_execution.py -q` |
| PostgreSQL integration command | `uv run --no-sync python -m pytest -n 4 --dist loadgroup tests/test_execution.py tests/test_sql_expansion_live.py -q` |

The focused command explicitly removes database URL overrides so it does not accidentally use a personal database. The PostgreSQL command is for the existing CI job with its disposable service and configured test environment only. The test fixture documentation requires `--dist loadgroup` for parallel shared-database tests or `-n 0` for serial runs. [VERIFIED: `tests/conftest.py:9-13,57-71`; `.github/workflows/ci.yml:225-266`]

The UI harness was run during this research: `node scripts/check_classroom_ui.mjs` passed 94 checks. It defaults to `classroom.js`, so it is a fast regression gate, not evidence for the tour or walkthrough script. [VERIFIED: `scripts/check_classroom_ui.mjs:1-5`; local command output]

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GUIDE-01 | Manual entry from home and workspace; manual describes controls, local initialization, and lesson switching | Browser acceptance plus existing UI route regression | `node scripts/check_classroom_ui.mjs`; disposable-browser check below | Yes, manual and harness exist; add coverage for content and both entry points. |
| GUIDE-02 | Tour start/dismiss/restart/completion preserves selection and draft and triggers no execution | Desktop browser integration | `work/browser-env/bin/python scripts/check_classroom_browser.py --url "$CLASSROOM_URL" --confirm-disposable --report work/phase1-browser-receipts.json` | Browser checker exists; add tour-specific acceptance assertions. |
| WALK-01 | Trace events link to source and expose bounded state/output, limit, and error behavior | Unit tests plus browser rendering | `.venv/bin/python -m pytest -n 0 tests/test_execution.py -q`; browser checker for visible trace | Backend test file exists; add trace contract assertions and visible-limit checks. |
| WALK-02 | SQL offsets/highlights correspond to supported PostgreSQL 17 results; unsupported input is safe | Planner unit tests and disposable database integration | PostgreSQL integration command above | Worker and live DB tests exist; add walkthrough-specific planner, offset, and before/after state tests. |
| WALK-04 | Walkthrough is distinct from Run; solution inspection leaves learner source unchanged | Backend regression and desktop browser integration for Python and SQL | Focused backend command above; disposable-browser command above | Run-preservation tests exist in `tests/test_learning_lab.py`; add step-through-specific draft/history assertions. |

### Sampling Rate

- **Per task commit:** `node scripts/check_classroom_ui.mjs` and the focused backend command when backend behavior changes.
- **Per wave merge:** disposable PostgreSQL integration command for SQL changes; disposable desktop-browser check for guide, tour, or walkthrough UI changes.
- **Phase gate:** All automated checks, PostgreSQL 17 integration, and desktop-browser acceptance green before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] Add Python walkthrough assertions for event/source mapping, state/output bounds, and limit/error behavior in `tests/test_execution.py`.
- [ ] Add SQL planner tests for source offsets and explicit unsupported/fallback behavior; add PostgreSQL 17 tests that verify results and database state before/after.
- [ ] Extend the browser checker to cover both manual entry paths, tour lifecycle and route neutrality, distinguishable Python/SQL walkthroughs, and solution inspection without draft replacement.
- [ ] Run browser acceptance only in a disposable classroom; the browser checker writes test pads/progress.

## Security Domain

Security enforcement is enabled at ASVS level 1. The applicable ASVS 5.0.0 categories are V1 Encoding and Sanitization, V2 Validation and Business Logic, V4 API and Web Service, and V8 Authorization. Authentication/session/cryptography behavior is not changed by this checkpoint. [VERIFIED: `.planning/config.json:49-51`; CITED: official OWASP ASVS 5.0.0 JSON and ASVS category index]

### Applicable ASVS Categories

| ASVS 5.0.0 category | Applies | Standard Control |
|---------------------|---------|-----------------|
| V1 Encoding and Sanitization | Yes | Render untrusted values as text; keep SQL injection controls and the restricted worker. [CITED: official OWASP ASVS 5.0.0 JSON; VERIFIED: `classroom-guide.js` rendering helpers; `step_through.py:609-664`] |
| V2 Validation and Business Logic | Yes | Validate walkthrough action, language, purpose, source size, timeout, cursor, and SQL plan at the trusted service layer. [CITED: official OWASP ASVS 5.0.0 JSON; VERIFIED: `lab.py:357-385`; `step_through.py:18-30,1026-1059`] |
| V4 API and Web Service | Yes | Preserve server-side action validation and ensure walkthrough responses do not bypass the ordinary persistence contract. [CITED: official OWASP ASVS category index; VERIFIED: `lab.py:345-410`] |
| V8 Authorization | Yes, for SQL worker authority | Retain the existing limited database role and worker checks; exercise them in disposable PostgreSQL tests. [CITED: official OWASP ASVS category index; VERIFIED: `step_through.py:609-664`] |
| Authentication, session management, cryptography | No new behavior | No authentication, session, key, or cryptographic feature is added in this phase. |
| Resource management | Yes | Preserve trace, output, variable, frame, SQL step, and database query bounds quoted above. [VERIFIED: `step_through.py:18-30,609-664`] |

### Known Threat Patterns for the Classroom Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Untrusted source or SQL exceeding validation/worker bounds | Denial of Service | Keep input, time, step, output, frame, and result caps; test over-limit paths. [VERIFIED: `lab.py:357-385`; `step_through.py:18-30`] |
| SQL injection or unintended write through walkthrough | Tampering | Keep the restricted PostgreSQL role, read-only transaction, parser subset, timeout, and before/after database-state tests. Read-only mode is not an absolute sandbox. [VERIFIED: `step_through.py:609-664`; CITED: PostgreSQL 17 transaction documentation] |
| HTML injection through displayed code, error, or result | Spoofing / Elevation of Privilege | Use safe text rendering and verify malicious-looking strings remain text in browser tests. [VERIFIED: `classroom-guide.js` rendering helpers] |
| Running tests against valuable learner state | Tampering / Denial of Service | Require disposable database/classroom targets and avoid volume cleanup except for a uniquely owned disposable project. [VERIFIED: `sql/AGENTS.md:20-25`; `docs/validation.md:433-448`] |

## Sources

### Primary (HIGH confidence)

- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` - phase decisions, active scope, requirements, and success criteria.
- `AGENTS.md`, `python/AGENTS.md`, `sql/AGENTS.md` - repository boundaries and Python/SQL constraints.
- `classroom.html`, `classroom.js`, `classroom-guide.js` - manual entry, navigation, tour, walkthrough request and presentation.
- `lab.py`, `execution.py`, `step_through.py`, `sql_readiness.py` - action contract, trace bounds, SQL planning, worker behavior, and preparation ordering.
- `tests/test_learning_lab.py`, `tests/test_execution.py`, `tests/conftest.py` - existing state-preservation and disposable PostgreSQL test patterns.
- `scripts/check_classroom_ui.mjs`, `scripts/check_classroom_browser.py`, `scripts/ci_classroom.py`, `.github/workflows/ci.yml`, `docs/validation.md` - existing automated validation and safe target requirements.
- `requirements/ci-browser.lock` - existing browser-only dependency pins.
- Local UI regression command and local runtime/tool probes.

### Secondary (MEDIUM confidence)

- [CITED: `https://www.postgresql.org/docs/17/sql-set-transaction.html`] - PostgreSQL read-only transaction semantics.
- [CITED: `https://www.postgresql.org/docs/17/hot-standby.html`] - PostgreSQL read-only behavior and limitations around side effects.
- [CITED: `https://playwright.dev/python/docs/intro`] - official Playwright Python/browser setup reference.
- [CITED: `https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.json`] - official ASVS 5.0.0 category and requirement text.
- [CITED: `https://cheatsheetseries.owasp.org/IndexASVS.html`] - ASVS 5.0.x category index, including V4 and V8 names.

### Tertiary (LOW confidence)

- None used for a recommendation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH for the existing project versions and source paths; MEDIUM for end-to-end availability because PostgreSQL and Chromium were not provisioned locally.
- Architecture: HIGH for the current code ownership and request flow; MEDIUM for behavior not yet exercised in a real browser/database during this research.
- Pitfalls: HIGH for source-visible route, dispatch, fallback, and preparation ordering; MEDIUM for PostgreSQL side-effect behavior until the phase integration checks run.

**Research date:** 2026-11-23
**Valid until:** 2026-12-23 for the stable code architecture; recheck package and registry details before any browser dependency installation or publication.
