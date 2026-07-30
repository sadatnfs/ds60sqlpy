# Bridge Day 2 — Solution notes

Attempt the [learner file](../lessons/day02_protocols_context_decorators.py)
before reading [day02_solution.py](day02_solution.py).

## Design

The reference context manager depends on a three-method `Connection` Protocol
and a callable factory Protocol. It acquires the resource before entering its
`try`, commits only after the body returns, rolls back if the body raises, and
closes in `finally`.

The decorator uses `ParamSpec` for all parameters and `TypeVar` for the return
type. `functools.wraps()` preserves runtime metadata. Log entries include only
the qualified function name and outcome; generic wrappers cannot know which
arguments are sensitive.

## Tradeoffs

- Catching `BaseException` ensures rollback during cancellation and keyboard
  interruption. Some applications catch `Exception` and rely on a lower-level
  owner for process-level cancellation cleanup. The ownership policy must be
  explicit either way.
- If rollback fails while handling an earlier body error, Python exception
  chaining can make diagnosis complicated. Production infrastructure may use
  `ExceptionGroup` or driver-managed transaction contexts to preserve both
  failures.
- A factory returning a Protocol is easy to fake. A pool lease is also a
  resource and may need “return to pool” rather than physical `close`.
- A decorator is convenient for uniform diagnostics, but explicit logging
  inside a workflow can include safer domain context and clearer timing.

## Verification

A recording fake makes order observable:

- success: `work`, `commit`, `close`;
- body failure: `work`, `rollback`, `close`;
- the same body exception reaches the caller.

Also verify the decorated function's name, return type, and exception behavior.
Do not assert timestamps or complete log formatting; those are incidental.

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day02_solution.py`; use it only after an honest attempt.

**Shared failure rule:** Logging arguments or allowing cleanup to suppress the original failure can violate both security and debugging contracts.

### Exercise 1 — Design

**Prompt:** Review the starter `Cursor` and `Connection` Protocols; minimize each boundary or
justify every retained method.

**Approach:** For `managed_connection`, only `commit`, `rollback`, and `close` are required;
cursor access belongs only if the manager itself uses it. Smaller structural types make fakes
simpler and prevent accidental coupling.

**Why this boundary matters:** A consumer Protocol should describe what the consumer calls, not
an entire driver object.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 2 — Implementation

**Prompt:** Implement `managed_connection(factory)` with acquire-once, yield-once,
commit-on-success, rollback-on-failure, re-raise, and close-in-finally behavior.

**Approach:** Call the factory before entering the `try`, yield the connection, and commit
afterward. Catch the chosen failure scope, roll back, use bare `raise`, and close in `finally`
so normal and exceptional exits share cleanup.

**Why this boundary matters:** Place closure in `finally`; keep commit after the yielded body
returns.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 3 — Testing

**Prompt:** Build a fake connection that records exact event order and test success, body
failure, rollback, and close.

**Approach:** A passing body records `work, commit, close`; a failing body records `work,
rollback, close` and the original exception escapes. The fake contains observations only and
makes no assertions itself.

**Why this boundary matters:** The order is part of the contract, so assert the entire event
list.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 4 — Implementation

**Prompt:** Implement `logged()` with `ParamSpec`, `TypeVar`, `functools.wraps`, and an injected
or module logger.

**Approach:** Create a wrapper with the same parameter pack, decorate it with `wraps(function)`,
log safe start/outcome fields, call the original, and return its value. The decorator's
annotated return is `Callable[P, R]`.

**Why this boundary matters:** Type wrapper parameters as `P.args`/`P.kwargs` and return the
original `R`.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 5 — Security

**Prompt:** Restrict decorator logs to function identity and outcome; prove arguments, keyword
values, return values, and connection representations are absent.

**Approach:** Log a stable function name and a success/failure marker only. Tests should pass
sentinel secrets through every value channel and assert those sentinels never appear in captured
records.

**Why this boundary matters:** Treat every callable value as potentially sensitive.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 6 — Typing

**Prompt:** Verify that decoration preserves name, docstring, return behavior, exception
identity, and a statically visible signature.

**Approach:** Assert `__name__`/`__wrapped__`, call the decorated function on success and
failure, and run the configured type checker against calls with correct and incorrect argument
shapes.

**Why this boundary matters:** `wraps` fixes runtime metadata; `ParamSpec` preserves the
type-level call shape.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 7 — Prediction

**Prompt:** Predict cleanup when the managed body raises `KeyboardInterrupt` or
cancellation-like `BaseException`; state whether your boundary catches it.

**Approach:** With `except BaseException`, rollback runs before the interruption is re-raised;
with `except Exception`, rollback may not run, though `finally` still closes. The reference
chooses broad cleanup while never translating interruption into success.

**Why this boundary matters:** The exception scope is a policy decision, but closure must still
be guaranteed.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 8 — Debugging

**Prompt:** Analyze what happens if rollback or close raises while a body exception is active,
and design a test that exposes exception masking.

**Approach:** A new exception from rollback/close normally becomes the visible exception and
chains the body failure in `__context__`. Record both events and choose an application
policy—often log cleanup failure safely while preserving the primary exception.

**Why this boundary matters:** Cleanup failures can replace the error that caused cleanup.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 9 — Design

**Prompt:** Compose two nested managed resources and decide which layer owns commit, rollback,
and close.

**Approach:** Use an outer owner for the connection transaction and inner managers for
subordinate cursors/resources that do not commit. Tests should show inner cleanup precedes the
outer commit or rollback.

**Why this boundary matters:** Exactly one layer should own each lifecycle transition.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 10 — Comparison

**Prompt:** Sketch the async equivalent and identify which operations require `await` and which
typing primitives change.

**Approach:** Use `@asynccontextmanager`, `AsyncIterator`, an awaitable factory, and await
commit/rollback/close. The success/failure ordering remains identical; only acquisition and
lifecycle calls become asynchronous.

**Why this boundary matters:** Preserve the same ownership state machine while changing the
execution protocol.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 11 — Typing

**Prompt:** Define a callable Protocol for the connection factory and compare it with
`Callable[[], Connection]` in tests and adapters.

**Approach:** A `Protocol` with `__call__() -> Connection` supports structural fakes and future
metadata, while `Callable` is sufficient for a simple zero-argument factory. Do not broaden the
return to a concrete driver class.

**Why this boundary matters:** Use a Protocol when the boundary needs attributes or overloads
beyond a bare call.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 12 — Extension

**Prompt:** Design a timing decorator with an injected monotonic clock while retaining the
no-argument/no-result logging policy.

**Approach:** Accept a `Callable[[], float]`, subtract start from finish in `finally`, and log
function identity, outcome, and duration only. Keep `ParamSpec`, `wraps`, and exception
propagation identical to `logged()`.

**Why this boundary matters:** Compute duration from two injected clock calls and emit a bounded
numeric field.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.
