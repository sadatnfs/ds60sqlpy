# Bridge Day 2 — Protocols, context managers, and decorators

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 1](day01_config_logging_cli.md)

## Why this matters

Application code should depend on the behavior it needs, not every method a
driver happens to expose. Small `Protocol` types document that behavior. A
context manager then gives one owner responsibility for commit, rollback, and
close. A carefully typed decorator can add diagnostics without changing the
caller's interface or logging sensitive arguments.

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

## Run the starter

```powershell
.\.venv\Scripts\python.exe bridge\lessons\day02_protocols_context_decorators.py
```

```bash
.venv/bin/python bridge/lessons/day02_protocols_context_decorators.py
```

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
2. **Implementation:** Implement `managed_connection(factory)` with acquire-once, yield-once,
   commit-on-success, rollback-on-failure, re-raise, and close-in-finally behavior.
   - **Progressive hint:** Place closure in `finally`; keep commit after the yielded body
     returns.
3. **Testing:** Build a fake connection that records exact event order and test success, body
   failure, rollback, and close.
   - **Progressive hint:** The order is part of the contract, so assert the entire event list.
4. **Implementation:** Implement `logged()` with `ParamSpec`, `TypeVar`, `functools.wraps`, and
   an injected or module logger.
   - **Progressive hint:** Type wrapper parameters as `P.args`/`P.kwargs` and return the
     original `R`.
5. **Security:** Restrict decorator logs to function identity and outcome; prove arguments,
   keyword values, return values, and connection representations are absent.
   - **Progressive hint:** Treat every callable value as potentially sensitive.
6. **Typing:** Verify that decoration preserves name, docstring, return behavior, exception
   identity, and a statically visible signature.
   - **Progressive hint:** `wraps` fixes runtime metadata; `ParamSpec` preserves the type-level
     call shape.
7. **Prediction:** Predict cleanup when the managed body raises `KeyboardInterrupt` or
   cancellation-like `BaseException`; state whether your boundary catches it.
   - **Progressive hint:** The exception scope is a policy decision, but closure must still be
     guaranteed.
8. **Debugging:** Analyze what happens if rollback or close raises while a body exception is
   active, and design a test that exposes exception masking.
   - **Progressive hint:** Cleanup failures can replace the error that caused cleanup.
9. **Design:** Compose two nested managed resources and decide which layer owns commit,
   rollback, and close.
   - **Progressive hint:** Exactly one layer should own each lifecycle transition.
10. **Comparison:** Sketch the async equivalent and identify which operations require `await`
   and which typing primitives change.
   - **Progressive hint:** Preserve the same ownership state machine while changing the
     execution protocol.
11. **Typing:** Define a callable Protocol for the connection factory and compare it with
   `Callable[[], Connection]` in tests and adapters.
   - **Progressive hint:** Use a Protocol when the boundary needs attributes or overloads beyond
     a bare call.
12. **Extension:** Design a timing decorator with an injected monotonic clock while retaining
   the no-argument/no-result logging policy.
   - **Progressive hint:** Compute duration from two injected clock calls and emit a bounded
     numeric field.

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

## Next step

[Day 3](day03_safe_psycopg_queries.md) uses a cursor Protocol to test SQL and
parameters separately. After your attempt, see
[the Day 2 solution notes](../solutions/day02_solutions.md).
