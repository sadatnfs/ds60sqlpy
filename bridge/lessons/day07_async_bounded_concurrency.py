"""Bridge Day 7: asyncio, bounded concurrency, and async database patterns.

Prerequisite: Bridge Day 6.
Read ``bridge/companion-guides/day07_async_bounded_concurrency.md`` first.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from contextlib import asynccontextmanager
from typing import Protocol, TypeVar

LESSON_ID = "bridge-07"
PREREQUISITES = ("bridge-06",)
LEVEL = "advanced"

T = TypeVar("T")
R = TypeVar("R")


class AsyncConnection(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def close(self) -> None: ...


@asynccontextmanager
async def managed_async_connection(
    factory: Callable[[], Awaitable[AsyncConnection]],
) -> AsyncIterator[AsyncConnection]:
    """Exercise 1: own an async transaction and close on every path."""

    raise NotImplementedError("implement async commit, rollback, and cleanup")
    yield  # pragma: no cover - keeps this an async generator while unfinished


async def map_bounded(
    items: Sequence[T],
    operation: Callable[[T], Awaitable[R]],
    *,
    limit: int,
) -> list[R]:
    """Exercise 2: bound in-flight work while preserving input order."""

    raise NotImplementedError("implement bounded structured concurrency")


async def fetch_customer_names(cursor: object, customer_ids: Sequence[int]) -> dict[int, str]:
    """Exercise 3: make one parameterized async PostgreSQL query."""

    raise NotImplementedError("define a small async cursor Protocol and execute safely")


def main() -> int:
    print("Bridge Day 7 starter loaded; no event loop or database was started.")
    print("Implement async resource ownership and measure maximum fake concurrency.")
    print("Do not add blocking calls such as time.sleep() inside async functions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
