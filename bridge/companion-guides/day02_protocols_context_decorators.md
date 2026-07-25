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

1. Review the starter `Cursor` and `Connection` Protocols. Remove any method your
   context manager does not actually need, or explain why the broader boundary
   is useful for the next exercise.
2. Implement `managed_connection(factory)`. Acquire once, yield once, commit
   only on success, roll back on failure, re-raise, and close in `finally`.
3. Build a fake connection that records event strings. Test exact ordering for
   success and failure.
4. Implement `logged()` with `ParamSpec`, `TypeVar`, `functools.wraps`, and an
   injected or module logger.
5. Log only function identity and outcome. Do not log positional arguments,
   keyword arguments, return values, or connection objects.
6. Test that the decorated callable preserves its name, return value, exception,
   and statically visible signature.

### Progressive hints

1. A generator-based manager needs `@contextmanager` and exactly one `yield`.
2. Put `close()` in a `finally` block.
3. `except BaseException` also protects cleanup during cancellation and
   keyboard interrupts; discuss whether your application wants that scope.
4. Type wrapper arguments as `P.args` and `P.kwargs`, then return `R`.

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

