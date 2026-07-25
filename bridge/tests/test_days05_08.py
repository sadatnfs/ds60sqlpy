"""Fast, fake-backed checks for bridge reference solutions Days 5–8."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal

import pytest

from bridge.scripts.validate_bridge import validate
from bridge.solutions.day05_solution import (
    FakeOrderRepository,
    customer_order_total,
    live_database_url,
    rollback_only,
)
from bridge.solutions.day06_solution import batches, load_sales, plan_load
from bridge.solutions.day07_solution import (
    fetch_customer_names,
    managed_async_connection,
    map_bounded,
)
from bridge.solutions.day08_solution import (
    JobRunner,
    Record,
    validate_database_transport,
)


class RollbackFake:
    def __init__(self) -> None:
        self.rollback_count = 0

    def rollback(self) -> None:
        self.rollback_count += 1


class BulkCursorFake:
    def __init__(self) -> None:
        self.calls: list[tuple[object, list[Sequence[object]]]] = []

    def executemany(
        self,
        query: object,
        params_seq: Iterable[Sequence[object]],
    ) -> None:
        self.calls.append((query, list(params_seq)))


class AsyncConnectionFake:
    def __init__(self) -> None:
        self.events: list[str] = []

    async def commit(self) -> None:
        self.events.append("commit")

    async def rollback(self) -> None:
        self.events.append("rollback")

    async def close(self) -> None:
        self.events.append("close")


class AsyncCursorFake:
    def __init__(self) -> None:
        self.call: tuple[object, object] | None = None

    async def execute(self, query: object, params: object = None) -> None:
        self.call = (query, params)

    async def fetchall(self) -> list[tuple[object, ...]]:
        return [(1, "Ada"), (2, "Grace")]


class ExtractorFake:
    def __init__(self, records: Sequence[Record]) -> None:
        self.records = records
        self.requested_checkpoints: list[int | None] = []

    def extract_after(self, checkpoint: int | None) -> list[Record]:
        self.requested_checkpoints.append(checkpoint)
        return [
            record for record in self.records if checkpoint is None or record.sequence > checkpoint
        ]


class SinkFake:
    def __init__(self, *, fail_on_call: int | None = None) -> None:
        self.fail_on_call = fail_on_call
        self.calls: list[list[Record]] = []

    def write(self, records: Sequence[Record]) -> None:
        self.calls.append(list(records))
        if self.fail_on_call == len(self.calls):
            raise RuntimeError("simulated sink failure")


class CheckpointFake:
    def __init__(self) -> None:
        self.value: int | None = None
        self.saved: list[int] = []

    def load(self) -> int | None:
        return self.value

    def save(self, checkpoint: int) -> None:
        self.value = checkpoint
        self.saved.append(checkpoint)


class MetricsFake:
    def __init__(self) -> None:
        self.events: list[tuple[str, int, dict[str, str]]] = []

    def increment(
        self,
        name: str,
        value: int = 1,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        self.events.append((name, value, dict(tags or {})))


def test_repository_fake_and_rollback_fixture() -> None:
    repository = FakeOrderRepository({7: [Decimal("10.20"), Decimal("2.30")]})
    assert customer_order_total(repository, 7) == Decimal("12.50")
    assert repository.requested_customer_ids == [7]

    connection = RollbackFake()
    with rollback_only(connection):
        pass
    assert connection.rollback_count == 1

    with pytest.raises(AssertionError, match="body failed"), rollback_only(connection):
        raise AssertionError("body failed")
    assert connection.rollback_count == 2

    assert live_database_url({"DS60_DATABASE_URL": "secret"}) is None
    assert (
        live_database_url(
            {"DS60_RUN_LIVE_DB_TESTS": "1", "DS60_DATABASE_URL": "postgresql://course"}
        )
        == "postgresql://course"
    )


def test_etl_validation_batching_and_bulk_parameters() -> None:
    plan = plan_load(
        [
            {
                "source_id": "sale-1",
                "customer_id": "7",
                "amount": "12.345",
                "occurred_on": "2026-01-02",
            },
            {
                "source_id": "sale-2",
                "customer_id": "not-an-int",
                "amount": "9.00",
                "occurred_on": "2026-01-03",
            },
        ]
    )
    assert [sale.source_id for sale in plan.accepted] == ["sale-1"]
    assert plan.accepted[0].amount == Decimal("12.34")
    assert [(row.source_id, row.reason) for row in plan.rejected] == [
        ("sale-2", "customer_id must be an integer")
    ]
    assert batches(plan.accepted, 2) == [plan.accepted]

    cursor = BulkCursorFake()
    assert load_sales(cursor, plan.accepted) == 1
    query, parameter_rows = cursor.calls[0]
    assert "%s" in str(query)
    assert parameter_rows[0][0] == "sale-1"


def test_bounded_async_work_preserves_order_and_limit() -> None:
    async def scenario() -> tuple[list[str], int]:
        active = 0
        maximum = 0

        async def operation(value: int) -> str:
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await asyncio.sleep(0)
            active -= 1
            return f"value-{value}"

        results = await map_bounded([3, 1, 2, 4], operation, limit=2)
        return results, maximum

    results, maximum = asyncio.run(scenario())
    assert results == ["value-3", "value-1", "value-2", "value-4"]
    assert maximum == 2


def test_async_connection_and_query_behavior() -> None:
    async def success_scenario() -> tuple[list[str], dict[int, str], tuple[object, object]]:
        connection = AsyncConnectionFake()
        async with managed_async_connection(lambda: _ready(connection)):
            connection.events.append("work")

        cursor = AsyncCursorFake()
        names = await fetch_customer_names(cursor, [2, 1])
        assert cursor.call is not None
        return connection.events, names, cursor.call

    async def _ready(connection: AsyncConnectionFake) -> AsyncConnectionFake:
        return connection

    events, names, call = asyncio.run(success_scenario())
    assert events == ["work", "commit", "close"]
    assert names == {1: "Ada", 2: "Grace"}
    assert call[1] == ([2, 1],)
    assert "%s" in str(call[0])

    async def failure_scenario() -> list[str]:
        connection = AsyncConnectionFake()
        with pytest.raises(RuntimeError, match="async failure"):
            async with managed_async_connection(lambda: _ready(connection)):
                connection.events.append("work")
                raise RuntimeError("async failure")
        return connection.events

    assert asyncio.run(failure_scenario()) == ["work", "rollback", "close"]


def test_capstone_checkpoints_only_after_successful_writes() -> None:
    records = [
        Record(1, "a", Decimal("1")),
        Record(2, "b", Decimal("2")),
        Record(3, "c", Decimal("3")),
        Record(4, "d", Decimal("4")),
    ]
    extractor = ExtractorFake(records)
    checkpoints = CheckpointFake()
    metrics = MetricsFake()

    failing_runner = JobRunner(
        job_name="sales",
        extractor=extractor,
        sink=SinkFake(fail_on_call=2),
        checkpoints=checkpoints,
        metrics=metrics,
        batch_size=2,
    )
    with pytest.raises(RuntimeError, match="simulated sink failure"):
        failing_runner.run_once()
    assert checkpoints.value == 2
    assert checkpoints.saved == [2]
    assert any(name == "job_failures" for name, _, _ in metrics.events)

    resumed_runner = JobRunner(
        job_name="sales",
        extractor=extractor,
        sink=SinkFake(),
        checkpoints=checkpoints,
        metrics=metrics,
        batch_size=2,
    )
    result = resumed_runner.run_once()
    assert result.records_read == 2
    assert result.records_written == 2
    assert result.checkpoint == 4
    assert checkpoints.saved == [2, 4]
    assert extractor.requested_checkpoints == [None, 2]


def test_capstone_requires_secure_remote_transport() -> None:
    validate_database_transport("postgresql://course@localhost/ds60")
    validate_database_transport("postgresql://course@db.example/ds60?sslmode=verify-full")
    with pytest.raises(ValueError, match="require TLS"):
        validate_database_transport("postgresql://course@db.example/ds60")
    with pytest.raises(ValueError, match="PostgreSQL URL"):
        validate_database_transport("sqlite:///course.db")


def test_capstone_validates_before_writing() -> None:
    sink = SinkFake()
    runner = JobRunner(
        job_name="sales",
        extractor=ExtractorFake([Record(1, "a", Decimal("-1"))]),
        sink=sink,
        checkpoints=CheckpointFake(),
        metrics=MetricsFake(),
    )
    with pytest.raises(ValueError, match="finite and positive"):
        runner.run_once()
    assert sink.calls == []


def test_bridge_artifact_contract() -> None:
    assert validate() == []
