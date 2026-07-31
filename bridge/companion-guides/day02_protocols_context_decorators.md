# Bridge Day 2 — Protocols, context managers, and decorators

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 1](day01_config_logging_cli.md)

## Why this matters

Application code should depend on the behavior it needs, not every method a
driver happens to expose. Small `Protocol` types document that behavior. A
context manager then gives one owner responsibility for commit, rollback, and
close. A carefully typed decorator can add diagnostics without changing the
caller's interface or logging sensitive arguments.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day02_protocols_context_decorators.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day02_protocols_context_decorators.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day02_protocols_context_decorators.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Objectives

By the end, you can:

- express structural interfaces with small `Protocol` classes;
- inject a connection factory rather than opening global resources;
- encode success, failure, and cleanup in a context manager;
- type a signature-preserving decorator with `ParamSpec` and `TypeVar`;
- verify resource ordering with a fake instead of a live database.

## Vocabulary

| Term | Meaning |
|---|---|
| structural typing | Compatibility based on available methods rather than explicit inheritance |
| Protocol | A typing construct that describes required behavior |
| dependency injection | Supplying an effectful dependency from outside the code that uses it |
| context manager | An object or generator that owns setup and cleanup around a `with` block |
| decorator | A callable that wraps another callable |
| `ParamSpec` | A type variable that captures a callable's complete parameter signature |


## Worked example: depend on one behavior

```python
from typing import Protocol


class Clock(Protocol):
    def monotonic(self) -> float: ...


def elapsed(clock: Clock, start: float) -> float:
    return clock.monotonic() - start
```

A production clock and a deterministic fake can both satisfy this Protocol
without inheriting from it. That is structural typing.

A resource context has four observable paths:

| Path | Required events |
|---|---|
| factory fails | propagate; there is no connection to close |
| body succeeds | commit, then close |
| body fails | rollback, re-raise, then close |
| commit or rollback fails | still attempt close; preserve useful failure context |

The starter focuses on the first three. The fourth is a stretch exercise because
multi-error reporting requires an explicit policy.


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: capability, ownership, and cross-cutting behavior

This lesson combines three features because each answers a different design
question. A `Protocol` asks, “What is the smallest capability this consumer
requires?” A context manager asks, “Who owns resource cleanup, and in what
order?” A decorator asks, “How can one policy wrap many callables without
changing their contract?” Keeping those questions separate prevents a wrapper
from becoming an untestable collection of hidden behavior.

A Protocol is structural: an object qualifies because it has the required
methods, not because it inherits from a course base class. This lets a real
Psycopg connection and a tiny recording fake satisfy the same consumer. Smaller
Protocols are easier to understand. If a context manager calls only `commit`,
`rollback`, and `close`, adding cursor creation or server metadata to its
Protocol gives the consumer powers it does not need.

Resource ownership is a state machine. Acquisition happens once before the
`yield`. A normal body return leads to commit and then close. A body failure
leads to rollback, re-raise, and then close. The event list is more useful than
a vague “it worked” assertion:

```python
events: list[str] = []


def record_success() -> None:
    events.append("work")
    events.append("commit")
    events.append("close")


record_success()
assert events == ["work", "commit", "close"]
```

Your fake should record events and return configured values; the test should
own assertions. A fake that asserts internally hides which behavior was
observed and makes reuse harder. Test both the success path and the first
failing path, because cleanup code often looks correct until the body raises.

Decorators introduce a typing and security boundary. `ParamSpec` preserves the
wrapped parameters, `TypeVar` preserves the return type, and
`functools.wraps()` preserves runtime metadata such as the name and docstring.
Logging every argument is not a helpful default: the decorator cannot know
which argument contains a password, payload, or personal data. Prefer function
identity, outcome, and safe bounded metadata. If richer domain context is
needed, add it explicitly at a layer that understands the data.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

## Exercises

### Practice contract

- **Focus:** Express resource ownership with small Protocols, a transaction-aware context manager, and a signature-preserving safe logger.
- **Assumptions:** The factory acquires exactly one connection; success commits; failure rolls back and re-raises; every path closes.
- **Primary failure mode:** Logging arguments or allowing cleanup to suppress the original failure can violate both security and debugging contracts.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **Design:** Review the starter `Cursor` and `Connection` Protocols; minimize each boundary or
   justify every retained method.
   - **Progressive hint:** A consumer Protocol should describe what the consumer calls, not an
     entire driver object.
   - **Verify:** List the exact members each consumer calls: the managed connection boundary needs only `commit`, `rollback`, and `close`; any retained cursor member must have a named caller.
2. **Implementation:** Implement `managed_connection(factory)` with acquire-once, yield-once,
   commit-on-success, rollback-on-failure, re-raise, and close-in-finally behavior.
   - **Progressive hint:** Place closure in `finally`; keep commit after the yielded body
     returns.
   - **Verify:** Assert success events are `acquire, body, commit, close`; failure events are `acquire, body, rollback, close`; and the original body exception reaches the caller.
3. **Testing:** Build a fake connection that records exact event order and test success, body
   failure, rollback, and close.
   - **Progressive hint:** The order is part of the contract, so assert the entire event list.
   - **Verify:** Configure a recording fake for one success and one body failure; compare the complete event lists and assert commit and rollback are mutually exclusive.
4. **Implementation:** Implement `logged()` with `ParamSpec`, `TypeVar`, `functools.wraps`, and
   an injected or module logger.
   - **Progressive hint:** Type wrapper parameters as `P.args`/`P.kwargs` and return the
     original `R`.
   - **Verify:** Decorate a typed two-argument function; assert its result is unchanged, its name and docstring survive, and logs contain qualified function name plus success/failure only.
5. **Security:** Restrict decorator logs to function identity and outcome; prove arguments,
   keyword values, return values, and connection representations are absent.
   - **Progressive hint:** Treat every callable value as potentially sensitive.
   - **Verify:** Pass sentinel positional/keyword values and a secret-bearing connection repr; assert none of them, nor the return value, appears in captured log records.
6. **Typing:** Verify that decoration preserves name, docstring, return behavior, exception
   identity, and a statically visible signature.
   - **Progressive hint:** `wraps` fixes runtime metadata; `ParamSpec` preserves the type-level
     call shape.
   - **Verify:** Compare `__name__`, `__doc__`, `inspect.signature`, returned value, and the identity of a raised exception before and after decoration; run the configured static type checker.
7. **Prediction:** Predict cleanup when the managed body raises `KeyboardInterrupt` or
   cancellation-like `BaseException`; state whether your boundary catches it.
   - **Progressive hint:** The exception scope is a policy decision, but closure must still be
     guaranteed.
   - **Verify:** Raise `KeyboardInterrupt` inside the managed body; assert rollback and close occur and the same interruption escapes rather than being converted to an ordinary error.
8. **Debugging:** Analyze what happens if rollback or close raises while a body exception is
   active, and design a test that exposes exception masking.
   - **Progressive hint:** Cleanup failures can replace the error that caused cleanup.
   - **Verify:** Make the body and rollback fail with different exception types, then make close fail in a separate case; inspect `__context__`/grouping so no cleanup failure is silently lost.
9. **Design:** Compose two nested managed resources and decide which layer owns commit,
   rollback, and close.
   - **Progressive hint:** Exactly one layer should own each lifecycle transition.
   - **Verify:** Record two nested resources and assert LIFO ownership: inner commit/rollback and close finish before the outer resource commits/rolls back and closes.
10. **Comparison:** Sketch the async equivalent and identify which operations require `await`
   and which typing primitives change.
   - **Progressive hint:** Preserve the same ownership state machine while changing the
     execution protocol.
   - **Verify:** Show an `asynccontextmanager` sketch where factory, commit, rollback, and close are awaited; identify `AsyncIterator` and async callable return types in the signature.
11. **Typing:** Define a callable Protocol for the connection factory and compare it with
   `Callable[[], Connection]` in tests and adapters.
   - **Progressive hint:** Use a Protocol when the boundary needs attributes or overloads beyond
     a bare call.
   - **Verify:** Run a type-checking example where both a named factory fake and a real adapter satisfy the callable Protocol; note the Protocol gives the boundary a reusable semantic name.
12. **Extension:** Design a timing decorator with an injected monotonic clock while retaining
   the no-argument/no-result logging policy.
   - **Progressive hint:** Compute duration from two injected clock calls and emit a bounded
     numeric field.
   - **Verify:** Inject clock values `10.0` and `10.25`; assert the timing record is `0.25` seconds while captured logs still omit arguments and return values.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


## Self-check

- Can an unrelated fake satisfy the Protocol without inheriting from it?
- Does a body exception remain the exception observed by the caller?
- Is `close` recorded exactly once on both normal and failing paths?
- Does the decorator preserve `__name__`?
- Could any log line reveal a database URL or customer record?

Expected behavior: the fake event list is `["work", "commit", "close"]` on
success and `["work", "rollback", "close"]` on body failure.

## Common pitfalls

- **Committing in `finally`:** that commits partial changes after failures.
- **Catching and suppressing exceptions:** callers may believe failed work
  succeeded.
- **Defining an enormous Protocol:** it couples fakes to behavior the function
  never uses.
- **Using `Callable[..., Any]`:** it discards the useful signature types.
- **Logging arguments in a generic decorator:** the wrapper cannot know which
  values contain passwords or personal data.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-01`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-02: Protocols Context Decorators.
Direct catalog prerequisites: bridge-01. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day02_protocols_context_decorators.md
Learner artifact: bridge/lessons/day02_protocols_context_decorators.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

[Day 3](day03_safe_psycopg_queries.md) uses a cursor Protocol to test SQL and
parameters separately. After your attempt, see
[the Day 2 solution notes](../solutions/day02_solutions.md).
