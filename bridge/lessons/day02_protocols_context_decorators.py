"""Bridge Day 2: Protocols, context managers, and typed decorators.

Prerequisite: Bridge Day 1.
Read ``bridge/companion-guides/day02_protocols_context_decorators.md`` first.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from typing import ParamSpec, Protocol, TypeVar

LESSON_ID = "bridge-02"
PREREQUISITES = ("bridge-01",)
LEVEL = "intermediate"

P = ParamSpec("P")
R = TypeVar("R")


class Cursor(Protocol):
    def execute(
        self,
        query: object,
        params: Sequence[object] | None = None,
    ) -> object: ...


class Connection(Protocol):
    def cursor(self) -> Cursor: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


@contextmanager
def managed_connection(factory: Callable[[], Connection]) -> Iterator[Connection]:
    """Core implementation: encode commit, rollback, and close ownership."""

    raise NotImplementedError("implement resource and transaction cleanup")
    yield  # pragma: no cover - keeps this function a generator while unfinished


def logged(
    function: Callable[P, R],
    *,
    logger: logging.Logger | None = None,
) -> Callable[P, R]:
    """Core implementation: preserve the wrapped signature and never log arguments."""

    raise NotImplementedError("implement a signature-preserving decorator")


# Exercises (answer-free)
# Focus: Express resource ownership with small Protocols, a transaction-aware context manager,
#    and a signature-preserving safe logger.
# Assumptions: The factory acquires exactly one connection; success commits; failure rolls back
#    and re-raises; every path closes.
# Failure to watch for: Logging arguments or allowing cleanup to suppress the original failure
#    can violate both security and debugging contracts.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Design] Review the starter `Cursor` and `Connection` Protocols; minimize each boundary or
#    justify every retained method.
#    Hint: A consumer Protocol should describe what the consumer calls, not an entire driver
#    object.
#    Verify: List the exact members each consumer calls: the managed connection boundary needs
#    only `commit`, `rollback`, and `close`; any retained cursor member must have a named
#    caller.
# 2. [Implementation] Implement `managed_connection(factory)` with acquire-once, yield-once,
#    commit-on-success, rollback-on-failure, re-raise, and close-in-finally behavior.
#    Hint: Place closure in `finally`; keep commit after the yielded body returns.
#    Verify: Assert success events are `acquire, body, commit, close`; failure events are
#    `acquire, body, rollback, close`; and the original body exception reaches the caller.
# 3. [Testing] Build a fake connection that records exact event order and test success, body
#    failure, rollback, and close.
#    Hint: The order is part of the contract, so assert the entire event list.
#    Verify: Configure a recording fake for one success and one body failure; compare the
#    complete event lists and assert commit and rollback are mutually exclusive.
# 4. [Implementation] Implement `logged()` with `ParamSpec`, `TypeVar`, `functools.wraps`, and
#    an injected or module logger.
#    Hint: Type wrapper parameters as `P.args`/`P.kwargs` and return the original `R`.
#    Verify: Decorate a typed two-argument function; assert its result is unchanged, its name
#    and docstring survive, and logs contain qualified function name plus success/failure only.
# 5. [Security] Restrict decorator logs to function identity and outcome; prove arguments,
#    keyword values, return values, and connection representations are absent.
#    Hint: Treat every callable value as potentially sensitive.
#    Verify: Pass sentinel positional/keyword values and a secret-bearing connection repr;
#    assert none of them, nor the return value, appears in captured log records.
# 6. [Typing] Verify that decoration preserves name, docstring, return behavior, exception
#    identity, and a statically visible signature.
#    Hint: `wraps` fixes runtime metadata; `ParamSpec` preserves the type-level call shape.
#    Verify: Compare `__name__`, `__doc__`, `inspect.signature`, returned value, and the
#    identity of a raised exception before and after decoration; run the configured static type
#    checker.
# 7. [Prediction] Predict cleanup when the managed body raises `KeyboardInterrupt` or
#    cancellation-like `BaseException`; state whether your boundary catches it.
#    Hint: The exception scope is a policy decision, but closure must still be guaranteed.
#    Verify: Raise `KeyboardInterrupt` inside the managed body; assert rollback and close occur
#    and the same interruption escapes rather than being converted to an ordinary error.
# 8. [Debugging] Analyze what happens if rollback or close raises while a body exception is
#    active, and design a test that exposes exception masking.
#    Hint: Cleanup failures can replace the error that caused cleanup.
#    Verify: Make the body and rollback fail with different exception types, then make close
#    fail in a separate case; inspect `__context__`/grouping so no cleanup failure is silently
#    lost.
# 9. [Design] Compose two nested managed resources and decide which layer owns commit, rollback,
#    and close.
#    Hint: Exactly one layer should own each lifecycle transition.
#    Verify: Record two nested resources and assert LIFO ownership: inner commit/rollback and
#    close finish before the outer resource commits/rolls back and closes.
# 10. [Comparison] Sketch the async equivalent and identify which operations require `await` and
#    which typing primitives change.
#    Hint: Preserve the same ownership state machine while changing the execution protocol.
#    Verify: Show an `asynccontextmanager` sketch where factory, commit, rollback, and close are
#    awaited; identify `AsyncIterator` and async callable return types in the signature.
# 11. [Typing] Define a callable Protocol for the connection factory and compare it with
#    `Callable[[], Connection]` in tests and adapters.
#    Hint: Use a Protocol when the boundary needs attributes or overloads beyond a bare call.
#    Verify: Run a type-checking example where both a named factory fake and a real adapter
#    satisfy the callable Protocol; note the Protocol gives the boundary a reusable semantic
#    name.
# 12. [Extension] Design a timing decorator with an injected monotonic clock while retaining the
#    no-argument/no-result logging policy.
#    Hint: Compute duration from two injected clock calls and emit a bounded numeric field.
#    Verify: Inject clock values `10.0` and `10.25`; assert the timing record is `0.25` seconds
#    while captured logs still omit arguments and return values.


def main() -> int:
    print("Bridge Day 2 starter loaded.")
    print("Implement the Protocol-backed context manager and typed decorator.")
    print("Test success, failure, cleanup, metadata, and return types with fakes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
