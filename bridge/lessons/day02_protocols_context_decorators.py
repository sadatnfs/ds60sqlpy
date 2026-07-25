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
    """Exercise 1: encode commit, rollback, and close ownership."""

    raise NotImplementedError("implement resource and transaction cleanup")
    yield  # pragma: no cover - keeps this function a generator while unfinished


def logged(
    function: Callable[P, R],
    *,
    logger: logging.Logger | None = None,
) -> Callable[P, R]:
    """Exercise 2: preserve the wrapped signature and never log arguments."""

    raise NotImplementedError("implement a signature-preserving decorator")


def main() -> int:
    print("Bridge Day 2 starter loaded.")
    print("Implement the Protocol-backed context manager and typed decorator.")
    print("Test success, failure, cleanup, metadata, and return types with fakes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
