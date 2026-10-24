"""Day 7 reference: bounded async work and async transaction ownership."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from contextlib import asynccontextmanager
from typing import Protocol, TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")


class AsyncConnection(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def close(self) -> None: ...


class AsyncReadCursor(Protocol):
    async def execute(
        self,
        query: object,
        params: Sequence[object] | None = None,
    ) -> object: ...

    async def fetchall(self) -> Sequence[Sequence[object]]: ...


@asynccontextmanager
async def managed_async_connection(
    factory: Callable[[], Awaitable[AsyncConnection]],
) -> AsyncIterator[AsyncConnection]:
    """Own one async connection with the same success/failure rules as Day 2."""

    connection = await factory()
    try:
        yield connection
    except BaseException:
        await connection.rollback()
        raise
    else:
        await connection.commit()
    finally:
        await connection.close()


async def map_bounded(
    items: Sequence[T],
    operation: Callable[[T], Awaitable[R]],
    *,
    limit: int,
) -> list[R]:
    """Run at most ``limit`` operations concurrently and preserve input order."""

    if limit < 1:
        raise ValueError("limit must be at least 1")

    semaphore = asyncio.Semaphore(limit)
    results: dict[int, R] = {}

    async def run_one(index: int, item: T) -> None:
        async with semaphore:
            results[index] = await operation(item)

    async with asyncio.TaskGroup() as task_group:
        for index, item in enumerate(items):
            task_group.create_task(run_one(index, item))

    return [results[index] for index in range(len(items))]


CUSTOMER_NAMES_SQL = """
SELECT customer_id, full_name
FROM training.customers
WHERE customer_id = ANY(%s)
ORDER BY customer_id
""".strip()


async def fetch_customer_names(
    cursor: AsyncReadCursor,
    customer_ids: Sequence[int],
) -> dict[int, str]:
    """Execute one async PostgreSQL round trip for a set of IDs."""

    if any(customer_id < 1 for customer_id in customer_ids):
        raise ValueError("customer IDs must be positive")
    if not customer_ids:
        return {}
    await cursor.execute(CUSTOMER_NAMES_SQL, (list(customer_ids),))
    return {int(cast(int, row[0])): str(row[1]) for row in await cursor.fetchall()}
