# Phase 1: Qualify 1.4.4 Guide & Python/SQL Walkthroughs - Pattern Map

**Mapped:** 2026-11-23
**Files analyzed:** 8 candidate existing files, including 3 conditional backend files
**Analogs found:** 8 / 8

Scope is the Phase 1 GUIDE-01, GUIDE-02, WALK-01, WALK-02, and WALK-04 checkpoint. The research calls for focused edits to the manual, guide client and acceptance tests. Backend edits are conditional on what the planner decides about SQL preparation side effects and unsupported-query behavior. No new source file is implied. Do not treat this phase as broader overhaul completion or publication.

All named source analogs below were checked with `git ls-files --error-unmatch`; none are ignored runtime mirrors.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/ds60sqlpy/assets/classroom.html` | component | request-response, navigation | Same file, manual entry and walkthrough sections | exact |
| `src/ds60sqlpy/assets/classroom-guide.js` | component | event-driven, request-response | Same file, `startWalk` and tour lifecycle | exact |
| `tests/test_execution.py` | test | request-response, transform, database | Same file, `live_database` and live SQL assertions | role-match; no step-through-specific test exists |
| `tests/test_learning_lab.py` | test | request-response, learner-state | Same file, worked-solution state-preservation test | exact |
| `scripts/check_classroom_browser.py` | test | request-response, browser interaction | Same file, `classroom_checks` and `Audit` | exact |
| `src/ds60sqlpy/step_through.py` | utility | transform, request-response | `plan_sql` and `python_response` | exact if backend behavior changes |
| `src/ds60sqlpy/execution.py` | service | request-response, file-I/O | `PadRunner.step_through` and `_step_through_sql` | exact if SQL response behavior changes |
| `src/ds60sqlpy/lab.py` | controller | request-response | `LabServer._step_through` | exact if SQL preparation ordering changes |

## Pattern Assignments

### `src/ds60sqlpy/assets/classroom.html` (component, request-response/navigation)

**Analog:** `src/ds60sqlpy/assets/classroom.html`

Keep the current manual as authored classroom HTML and use the existing IDs and route links. The home manual and tour links already exist (`classroom.html:61, 101`); the workspace tour entry is at line 139 and the manual tour action at line 754.

**Manual command pattern** (`classroom.html:945-974`):

```html
<dt>First time on this computer</dt>
<dd><code>./classroom doctor</code> then <code>./classroom</code></dd>
<dt>Smaller download (Python, SQL and a few more)</dt>
<dd><code>./classroom --starter</code></dd>
<dt>Use the published images instead of building</dt>
<dd><code>./classroom --all --from-hub sadatnfs --tag 1.4.4</code></dd>
```

The existing Hub owner/tag is specifically unverified. Do not repeat it as an approved target. Keep the local Docker entry point useful, and do not infer a replacement owner or tag. Stable IDs such as `manual-start`, `manual-switch`, and `manual-step` are navigation anchors; preserve them.

**Walkthrough and solution-copy pattern** (`classroom.html:1043-1087`):

```html
<dt>Step through the solution</dt>
<dd>Walks through the worked answer one step at a time (Python and SQL).</dd>
...
<strong>Step through</strong> runs your code slowly, one step at a time, so you can
see what the computer does instead of only the final answer. It works in Python and
SQL lessons.
...
Stepping never saves your code or records a run, so it is safe to experiment.
```

The current wording describes a Python/SQL distinction and a no-save guarantee. Qualify those claims against parser behavior, SQL course-database preparation, and tests rather than broadening them to all PostgreSQL syntax or guaranteeing no setup side effects.

### `src/ds60sqlpy/assets/classroom-guide.js` (component, event-driven/request-response)

**Analog:** `src/ds60sqlpy/assets/classroom-guide.js`

**Imports/shared browser globals** (`classroom-guide.js:1-14`): this asset is an IIFE and consumes shared globals established by `classroom.js`; preserve that load order and avoid a second UI implementation.

**Walkthrough request pattern** (`classroom-guide.js:150-180`):

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

`code` is a source snapshot, and the action is distinct from Run. Solution inspection reads `solutionCode(view)` while practice reads `#source`; keep those paths separate and do not copy solution source into the learner editor.

**UI safety and error handling** (`classroom-guide.js:7-12, 175-190`):

```javascript
const make = (tag, text, cls) => {
  const item = document.createElement(tag);
  if (text !== undefined && text !== null) item.textContent = text;
  if (cls) item.className = cls;
  return item;
};
...
} catch (error) {
  if (ticket !== sequence) return;
  showMessage("Step-through could not start. " + error.message, true);
  title.focus();
}
```

Continue using `textContent` for learner code, SQL results, and errors. Keep asynchronous responses bound to the lesson/ticket that initiated them.

**Tour lifecycle and route-neutrality target** (`classroom-guide.js:550-800`):

```javascript
function startTour(back = document.activeElement) {
  if (tour || typeof current !== "object" || !current) return;
  if (manualOpen) return;
  ...
  tour = { layer, spot, card, steps, index: 0, back, onMove };
  ...
}
```

The existing `tourFromAnywhere` fallback (`classroom-guide.js:758-771`) selects Python or the first subject and calls `switchTrack` if there is no lesson. Research identifies this as the home-tour selection side effect. Change/restrict that route without making tour start, dismiss, restart, or completion select a subject or lesson. Reuse the existing overlay creation, Escape/finish handling, and focus restoration.

### `tests/test_execution.py` (test, request-response/transform/database)

**Analog:** `tests/test_execution.py`

There are no current `step_through` tests in this file. Reuse the pure-function/unit-test organization for bounds, source spans, events, errors, and output, then use the opt-in PostgreSQL fixture only for actual SQL result and before/after state assertions.

**Disposable database fixture** (`tests/test_execution.py:450-476`):

```python
target = os.environ.get("DS60_TEST_DATABASE_URL")
if not target:
    pytest.skip("Set DS60_TEST_DATABASE_URL for the explicitly disposable local database")
validate_course_database_target(target)
psycopg = pytest.importorskip("psycopg")
role = "testpad_" + uuid.uuid4().hex
...
monkeypatch.setenv("DS60_DATABASE_URL", limited_target)
yield LiveDatabase(psycopg, limited_target, schema, target)
```

Preserve the opt-in disposable target, course-database validation, limited role, and fixture cleanup. Do not run these tests against learner or shared data.

**Existing live SQL assertion pattern** (`tests/test_execution.py:478-519`):

```python
result = PadRunner(course).run(
    "python-01",
    "sql",
    "CREATE TEMP TABLE pad_local (n int); "
    "INSERT INTO pad_local VALUES (5); SELECT * FROM pad_local; "
    "SELECT generate_series(1, 102) AS n;",
)
assert result["returncode"] == 0, result["output"]
payload = json.loads(result["output"])
assert payload["results"][2]["rows"] == [[5]]
```

For WALK-02, assert source offsets/highlights against planner steps and verify query output plus pre/post database state in the explicitly disposable PostgreSQL 17 service. Avoid mutating learner tables. Test supported and rejected inputs, but include planner fallback: `step_through.py:1053-1059` turns `_Fallback` into a whole-query step, not an `unsupported` result.

### `tests/test_learning_lab.py` (test, request-response/learner-state)

**Analog:** `tests/test_learning_lab.py`

**Imports and isolated setup** (`tests/test_learning_lab.py:1-20, 191-202`): existing tests use `tmp_path`, a private local catalog, `LabServer`, and `PadRunner`. Keep new service tests in this pytest style and direct writes to temporary state.

**Solution source, pad, and history preservation** (`tests/test_learning_lab.py:191-217`):

```python
def no_receipt(*args: object, **kwargs: object) -> None:
    raise AssertionError("A worked-solution run must not create a learner run receipt.")


monkeypatch.setattr(server._classroom.runs, "record", no_receipt)
...
result = server.action({"action": "run", **scope, "code": "print(6 * 7)\n", "purpose": "solution"})
assert server.action({"action": "read-pad", **scope})["code"] == "print('mine')\n"
assert server.action({"action": "pad-history", **scope})["history"] == []
```

Extend this contract for `step-through` and both supported languages as applicable: source, progress, receipts, and history remain unchanged, and the solution walkthrough is distinct from ordinary Run. Tests should call the actual `LabServer.action` boundary rather than a mock-only route.

### `scripts/check_classroom_browser.py` (test, request-response/browser interaction)

**Analog:** `scripts/check_classroom_browser.py`

**Harness and disposable-target guard** (`check_classroom_browser.py:1-8, 650-664`): this script uses real Chromium and classroom HTTP responses; it rejects a non-fixtures run without `--url` and `--confirm-disposable`. Keep browser evidence in this checker, never against a learner classroom.

**Real classroom route and saved-work pattern** (`check_classroom_browser.py:238-350, 385-395`):

```python
page.goto(origin + "/classroom")
...
page.locator(SOURCE_EDITOR).fill(python_source)
page.locator("#phase-note").fill(NOTE)
save(page, expect)
...
expect(page.locator("#source")).to_have_value(python_source)
expect(page.locator("#phase-note")).to_have_value(NOTE)
```

Extend `classroom_checks` to verify both manual entry paths, tour start/dismiss/restart/finish, and no-selection home behavior. Seed and compare the selected lesson, draft, notes, and relevant run state before and after. Observe requests so tour actions issue neither Run nor `step-through`; walkthroughs should visibly exercise the distinct action for Python and SQL and preserve the original draft during solution inspection. The checker writes test work, so retain `--confirm-disposable` and the `work/` report boundary.

### Conditional backend files

These are not unconditional edits in the research recommendation. The planner should include them only if implementation or acceptance needs a server-side change.

#### `src/ds60sqlpy/step_through.py` (utility, transform/request-response)

**Analog:** `src/ds60sqlpy/step_through.py`

**Bounds and response shape** (`step_through.py:18-30, 748-847`):

```python
MAX_STEPS = 400
OUTPUT_CAP = 65_536
MAX_SQL_STEPS = 40
...
return {
    "kind": "python",
    "code": code,
    "steps": steps,
    "output": output,
    "step_limit_reached": step_limit,
    "stopped": stopped,
    "error": error,
    "elapsed_seconds": elapsed_seconds,
}
```

Preserve bounded traces and structured line/event/stack/local/output/error fields. Test the existing contract before changing trace execution.

**SQL source offsets and fallback** (`step_through.py:1026-1059`):

```python
if cursor_offset is not None:
    for span in spans:
        if span[0] <= cursor_offset <= span[2]:
            chosen = span
...
except _Fallback:
    steps, unsupported = [_whole_step(statement)], None
```

Use the planner's actual offsets. Do not label every parser fallback unsupported, nor claim a complete PostgreSQL grammar.

#### `src/ds60sqlpy/execution.py` (service, request-response/file-I/O)

**Analog:** `src/ds60sqlpy/execution.py`

**Existing dispatch and request validation** (`execution.py:678-714`):

```python
"""Trace Python line by line, or walk one SELECT clause by clause, without saving."""

...
if definition.executor == "python":
    return self._step_through_python(path.parent, code, limit)
return self._step_through_sql(path.parent, lesson_id, code, cursor_offset, limit)
```

Preserve input-size and timeout validation, Python-versus-SQL dispatch, and the no-save contract. For SQL, `_step_through_sql` plans before writing temporary step/result files (`execution.py:753-780`). Reuse that separation and existing worker rather than creating a second parser or executor.

#### `src/ds60sqlpy/lab.py` (controller, request-response)

**Analog:** `src/ds60sqlpy/lab.py`

**Action validation and dispatch** (`lab.py:357-410`):

```python
"""Trace a pad without saving it, writing a receipt or touching its history."""

...
preparation = (
    ensure_before_run(self.catalog, lesson_id)
    if language == "sql" or uses_course_database(lesson)
    else None
)
response = self.pads.step_through(...)
```

The SQL course setup currently runs before `PadRunner.step_through` parses source. The research leaves open whether unsupported input may cause that one-time preparation. If the acceptance contract forbids even preparation effects, plan and validate before `ensure_before_run`; otherwise explicitly test against an already prepared disposable fixture and distinguish setup from query effects. Keep input/action/purpose checks and the no-receipt/no-history path.

## Shared Patterns

### Stable lesson identity and scope

**Apply to:** manual routes, tour lifecycle, backend requests, and browser assertions.

Preserve current lesson IDs, the existing `/classroom` routes, and state namespaces. Phase 1 only qualifies the unfinished 1.4.4 checkpoint. Python and SQL are checkpoints, not the boundary of the wider track coverage.

### No-save walkthrough boundary

**Sources:** `classroom-guide.js:150-180`; `lab.py:357-410`; `tests/test_learning_lab.py:191-217`.

The browser sends a distinct `step-through` request with a source snapshot and explicit `practice` or `solution` purpose. The backend returns trace data without saving a pad, receipt, or history. Keep Run separate and assert saved source and existing learner state before/after.

### SQL safety and honest support claims

**Sources:** `step_through.py:18-30,1026-1059`; `execution.py:753-780`; `lab.py:393-404`; `tests/test_execution.py:450-519`.

Use bounded inputs, existing planner offsets, and the restricted PostgreSQL worker. Unknown constructs can fall back to a whole-query step, and SQL preparation currently precedes parsing at the lab boundary. Define any documented SQL subset from tested planner cases and PostgreSQL 17 behavior. Compare database state in disposable tests; read-only mode alone is not a guarantee against all side effects. Do not execute SQL against learner data.

### Browser acceptance isolation

**Source:** `scripts/check_classroom_browser.py:1-8,650-664`.

Use the existing real-browser checker only with an explicitly disposable classroom and `--confirm-disposable`. Do not stop unrelated containers or delete learner volumes. Runtime builds, image scans, publication, and cleanup remain separate gates.

## No Analog Found

No phase source file lacks an analog. No new source files are implied by the research artifact. There is no existing focused step-through test in `tests/test_execution.py`, so follow its existing pure unit-test and opt-in live PostgreSQL test structure rather than copying a nonexistent test.

## Metadata

**Analog search scope:** `src/ds60sqlpy/assets/`, `src/ds60sqlpy/`, `tests/`, `scripts/`, phase research, and project/subject instructions.
**Files scanned:** 8 named candidates plus surrounding test and browser harness sections.
**Pattern extraction date:** 2026-11-23
