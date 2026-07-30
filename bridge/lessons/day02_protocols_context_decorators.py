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
# 2. [Implementation] Implement `managed_connection(factory)` with acquire-once, yield-once,
#    commit-on-success, rollback-on-failure, re-raise, and close-in-finally behavior.
#    Hint: Place closure in `finally`; keep commit after the yielded body returns.
# 3. [Testing] Build a fake connection that records exact event order and test success, body
#    failure, rollback, and close.
#    Hint: The order is part of the contract, so assert the entire event list.
# 4. [Implementation] Implement `logged()` with `ParamSpec`, `TypeVar`, `functools.wraps`, and
#    an injected or module logger.
#    Hint: Type wrapper parameters as `P.args`/`P.kwargs` and return the original `R`.
# 5. [Security] Restrict decorator logs to function identity and outcome; prove arguments,
#    keyword values, return values, and connection representations are absent.
#    Hint: Treat every callable value as potentially sensitive.
# 6. [Typing] Verify that decoration preserves name, docstring, return behavior, exception
#    identity, and a statically visible signature.
#    Hint: `wraps` fixes runtime metadata; `ParamSpec` preserves the type-level call shape.
# 7. [Prediction] Predict cleanup when the managed body raises `KeyboardInterrupt` or
#    cancellation-like `BaseException`; state whether your boundary catches it.
#    Hint: The exception scope is a policy decision, but closure must still be guaranteed.
# 8. [Debugging] Analyze what happens if rollback or close raises while a body exception is
#    active, and design a test that exposes exception masking.
#    Hint: Cleanup failures can replace the error that caused cleanup.
# 9. [Design] Compose two nested managed resources and decide which layer owns commit, rollback,
#    and close.
#    Hint: Exactly one layer should own each lifecycle transition.
# 10. [Comparison] Sketch the async equivalent and identify which operations require `await` and
#    which typing primitives change.
#    Hint: Preserve the same ownership state machine while changing the execution protocol.
# 11. [Typing] Define a callable Protocol for the connection factory and compare it with
#    `Callable[[], Connection]` in tests and adapters.
#    Hint: Use a Protocol when the boundary needs attributes or overloads beyond a bare call.
# 12. [Extension] Design a timing decorator with an injected monotonic clock while retaining the
#    no-argument/no-result logging policy.
#    Hint: Compute duration from two injected clock calls and emit a bounded numeric field.


def main() -> int:
    print("Bridge Day 2 starter loaded.")
    print("Implement the Protocol-backed context manager and typed decorator.")
    print("Test success, failure, cleanup, metadata, and return types with fakes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
