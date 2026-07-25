"""Fast, fake-backed checks for bridge reference solutions Days 1–4."""

from __future__ import annotations

import logging
from decimal import Decimal

import pytest

from bridge.solutions.day01_solution import (
    Settings,
    load_settings,
    redact_database_url,
)
from bridge.solutions.day02_solution import managed_connection, normalize_customer_name
from bridge.solutions.day03_solution import Customer, find_customers
from bridge.solutions.day04_solution import (
    RetryPolicy,
    TransientDatabaseError,
    create_job_once,
    run_in_transaction,
    run_with_retry,
)


class FakeConnection:
    def __init__(self) -> None:
        self.events: list[str] = []

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")

    def close(self) -> None:
        self.events.append("close")


class RecordingReadCursor:
    def __init__(self, rows: list[tuple[object, ...]]) -> None:
        self.rows = rows
        self.calls: list[tuple[object, object]] = []

    def execute(self, query: object, params: object = None) -> None:
        self.calls.append((query, params))

    def fetchall(self) -> list[tuple[object, ...]]:
        return self.rows


class RecordingWriteCursor:
    def __init__(self, row: tuple[object, ...] | None) -> None:
        self.row = row
        self.calls: list[tuple[object, object]] = []

    def execute(self, query: object, params: object = None) -> None:
        self.calls.append((query, params))

    def fetchone(self) -> tuple[object, ...] | None:
        return self.row


def test_settings_precedence_validation_and_redaction() -> None:
    settings = load_settings(
        {
            "DS60_DATABASE_URL": "postgresql://env:secret@localhost/course",
            "DS60_LOG_LEVEL": "warning",
        },
        database_url="postgresql://cli:top-secret@db.example:5432/course?sslmode=require",
        log_level="error",
        dry_run=True,
    )

    assert settings == Settings(
        "postgresql://cli:top-secret@db.example:5432/course?sslmode=require",
        "ERROR",
        True,
    )
    safe = redact_database_url(settings.database_url)
    assert safe == "postgresql://cli:***@db.example:5432/course"
    assert "top-secret" not in safe
    assert "sslmode" not in safe

    with pytest.raises(ValueError, match="invalid log level"):
        load_settings({}, log_level="verbose")


def test_managed_connection_commits_or_rolls_back_then_closes() -> None:
    successful = FakeConnection()
    with managed_connection(lambda: successful):
        successful.events.append("work")
    assert successful.events == ["work", "commit", "close"]

    failed = FakeConnection()
    with (
        pytest.raises(RuntimeError, match="boom"),
        managed_connection(lambda: failed),
    ):
        failed.events.append("work")
        raise RuntimeError("boom")
    assert failed.events == ["work", "rollback", "close"]


def test_typed_decorator_preserves_behavior_and_metadata(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    assert normalize_customer_name("  ada   lovelace ") == "Ada Lovelace"
    assert normalize_customer_name.__name__ == "normalize_customer_name"
    assert "starting function=" in caplog.text
    assert "ada" not in caplog.text


def test_query_values_are_bound_separately() -> None:
    cursor = RecordingReadCursor([(7, "Ada", Decimal("123.45"))])
    customers = find_customers(
        cursor,
        country="US' OR true --",
        minimum_lifetime_value=Decimal("10.00"),
    )

    assert customers == [Customer(7, "Ada", Decimal("123.45"))]
    query, params = cursor.calls[0]
    assert "%s" in str(query)
    assert "US' OR true --" not in str(query)
    assert params == ("US' OR true --", Decimal("10.00"))


def test_idempotent_insert_uses_one_parameterized_statement() -> None:
    inserted = RecordingWriteCursor((42,))
    assert create_job_once(inserted, idempotency_key="source:7", payload="{}") == 42
    assert inserted.calls[0][1] == ("source:7", "{}")
    assert "ON CONFLICT" in str(inserted.calls[0][0])

    duplicate = RecordingWriteCursor(None)
    assert create_job_once(duplicate, idempotency_key="source:7", payload="{}") is None


def test_transaction_and_retry_boundaries_are_deterministic() -> None:
    connection = FakeConnection()
    assert run_in_transaction(connection, lambda: 9) == 9
    assert connection.events == ["commit"]

    failed_connection = FakeConnection()

    def fail_transaction() -> int:
        raise LookupError("transaction failed")

    with pytest.raises(LookupError, match="transaction failed"):
        run_in_transaction(failed_connection, fail_transaction)
    assert failed_connection.events == ["rollback"]

    attempts = 0
    delays: list[float] = []

    def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TransientDatabaseError("temporary")
        return "ok"

    result = run_with_retry(
        flaky,
        policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.25),
        sleep=delays.append,
    )
    assert result == "ok"
    assert attempts == 3
    assert delays == [0.25, 0.5]

    with pytest.raises(ValueError, match="permanent"):
        run_with_retry(
            lambda: (_ for _ in ()).throw(ValueError("permanent")),
            sleep=delays.append,
        )

    with pytest.raises(ValueError, match="at least 1"):
        RetryPolicy(max_attempts=0)
