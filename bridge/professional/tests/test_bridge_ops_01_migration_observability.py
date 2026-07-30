"""Fake-backed checks for BRIDGE-OPS-01; no database or network is used."""

from __future__ import annotations

import ast
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from bridge.professional.solutions.bridge_ops_01_migration_observability_solution import (
    CREATE_METADATA_SQL,
    READ_ALL_SQL,
    READ_ONE_SQL,
    RECORD_MIGRATION_SQL,
    DeliveryResult,
    JsonEventLogger,
    Migration,
    ReadinessResult,
    RecoveryDecision,
    RecoveryEvidence,
    RetryableDatabaseError,
    RetryPolicy,
    SqlCommand,
    check_readiness,
    decide_recovery,
    deliver_migrations,
    plan_pending,
    redact_fields,
    require_course_database_url,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LEARNER_PATH = (
    REPOSITORY_ROOT
    / "bridge"
    / "professional"
    / "lessons"
    / "bridge_ops_01_migration_observability.py"
)
GUIDE_PATH = (
    REPOSITORY_ROOT
    / "bridge"
    / "professional"
    / "companion-guides"
    / "bridge_ops_01_migration_observability.md"
)


class FakeResult:
    def __init__(self, rows: Sequence[Sequence[object]] = ()) -> None:
        self._rows = list(rows)

    def fetchone(self) -> Sequence[object] | None:
        return None if not self._rows else self._rows[0]

    def fetchall(self) -> Sequence[Sequence[object]]:
        return list(self._rows)


@dataclass
class SharedDatabase:
    metadata_exists: bool = False
    applied: dict[str, str] = field(default_factory=dict)
    committed_commands: list[tuple[str, tuple[object, ...]]] = field(default_factory=list)
    fail_once_for_query: str | None = None
    query_failed: bool = False
    fail_migration_commit_once: bool = False
    migration_commit_failed: bool = False


class FakeSession:
    def __init__(self, shared: SharedDatabase) -> None:
        self.shared = shared
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.events: list[str] = []
        self._pending_metadata = False
        self._pending_applied: tuple[str, str] | None = None
        self._pending_commands: list[tuple[str, tuple[object, ...]]] = []

    def execute(
        self,
        query: str,
        params: Sequence[object] | None = None,
    ) -> FakeResult:
        bound = tuple(params or ())
        self.calls.append((query, bound))

        if self.shared.fail_once_for_query == query and not self.shared.query_failed:
            self.shared.query_failed = True
            raise RetryableDatabaseError("temporary test failure with secret detail")
        if query == CREATE_METADATA_SQL:
            self._pending_metadata = True
            return FakeResult()
        if query == READ_ONE_SQL:
            checksum = self.shared.applied.get(str(bound[0]))
            return FakeResult(() if checksum is None else ((checksum,),))
        if query == RECORD_MIGRATION_SQL:
            self._pending_applied = (str(bound[0]), str(bound[1]))
            return FakeResult()
        if query == READ_ALL_SQL:
            return FakeResult(sorted(self.shared.applied.items()))
        if query == "SELECT 1":
            return FakeResult(((1,),))
        if query == "SELECT to_regclass(%s)":
            table = "training.ds60_schema_migrations" if self.shared.metadata_exists else None
            return FakeResult(((table,),))
        if query.startswith("SELECT pg_advisory_xact_lock"):
            return FakeResult(((None,),))
        if query.startswith("SELECT %s = %s"):
            return FakeResult(((bound[0] == bound[1],),))

        self._pending_commands.append((query, bound))
        return FakeResult()

    def commit(self) -> None:
        self.events.append("commit")
        if self._pending_metadata:
            self.shared.metadata_exists = True
        if self._pending_applied is not None:
            migration_id, checksum = self._pending_applied
            self.shared.applied[migration_id] = checksum
            self.shared.committed_commands.extend(self._pending_commands)
            if self.shared.fail_migration_commit_once and not self.shared.migration_commit_failed:
                self.shared.migration_commit_failed = True
                raise RetryableDatabaseError("commit outcome was uncertain")

    def rollback(self) -> None:
        self.events.append("rollback")
        self._pending_metadata = False
        self._pending_applied = None
        self._pending_commands.clear()

    def close(self) -> None:
        self.events.append("close")


class FakeSessionFactory:
    def __init__(self, shared: SharedDatabase) -> None:
        self.shared = shared
        self.sessions: list[FakeSession] = []

    def __call__(self) -> FakeSession:
        session = FakeSession(self.shared)
        self.sessions.append(session)
        return session


class EventCollector:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def emit(self, event: str, fields: Mapping[str, object]) -> None:
        self.events.append((event, dict(fields)))


class MetricCollector:
    def __init__(self) -> None:
        self.counters: list[tuple[str, int, dict[str, str]]] = []
        self.observations: list[tuple[str, float, dict[str, str]]] = []

    def increment(
        self,
        name: str,
        value: int = 1,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        self.counters.append((name, value, dict(tags or {})))

    def observe(
        self,
        name: str,
        value: float,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        self.observations.append((name, value, dict(tags or {})))


def sample_migration() -> Migration:
    return Migration(
        migration_id="20260730_001_test_state",
        description="Set deterministic fake-backed state",
        commands=(
            SqlCommand(
                "UPDATE training.bridge_release_lab SET event_name = %s",
                ("ready",),
            ),
        ),
        verification=SqlCommand("SELECT %s = %s", ("ready", "ready")),
    )


def test_learner_contract_and_guide_headings() -> None:
    source = LEARNER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(LEARNER_PATH))
    assignments = {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {"LESSON_ID", "PREREQUISITES", "LEVEL"}
    }
    assert assignments == {
        "LESSON_ID": "bridge-ops-01",
        "PREREQUISITES": ("sql-found-02", "bridge-04", "bridge-05", "bridge-08"),
        "LEVEL": "advanced",
    }
    assert "bridge.professional.solutions" not in source

    guide = GUIDE_PATH.read_text(encoding="utf-8")
    headings = (
        "## Level and prerequisites",
        "## Learning objectives",
        "## Vocabulary and concepts",
        "## Worked example / walkthrough",
        "## Exercises",
        "## Self-check",
        "## Common pitfalls",
        "## Next step",
    )
    positions = [guide.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_sql_commands_keep_injection_shaped_values_separate() -> None:
    shaped_value = "ready'; DROP SCHEMA training CASCADE; --"
    command = SqlCommand(
        "UPDATE training.bridge_release_lab SET event_name = %s",
        (shaped_value,),
    )
    assert shaped_value not in command.text
    assert command.params == (shaped_value,)
    with pytest.raises(ValueError, match="one separate parameter"):
        SqlCommand("SELECT %s", ())


def test_plan_rejects_reordering_unknown_history_and_checksum_drift() -> None:
    first = sample_migration()
    second = Migration(
        migration_id="20260730_002_test_state",
        description="Add a second deterministic state",
        commands=(SqlCommand("SELECT 2"),),
        verification=SqlCommand("SELECT %s = %s", (2, 2)),
    )
    assert plan_pending((first, second), {}) == (first, second)
    assert plan_pending((first, second), {first.migration_id: first.checksum}) == (second,)

    with pytest.raises(ValueError, match="immutable ID order"):
        plan_pending((second, first), {})
    with pytest.raises(ValueError, match="unknown migration"):
        plan_pending((first,), {"20260729_999_unknown": "checksum"})
    with pytest.raises(ValueError, match="checksum drift"):
        plan_pending((first,), {first.migration_id: "changed"})


def test_delivery_retries_fresh_transaction_and_emits_safe_dimensions() -> None:
    migration = sample_migration()
    shared = SharedDatabase(fail_once_for_query=migration.commands[0].text)
    factory = FakeSessionFactory(shared)
    logger = EventCollector()
    metrics = MetricCollector()
    delays: list[float] = []
    clock_values = iter((10.0, 10.75))

    result = deliver_migrations(
        factory,
        (migration,),
        request_id="change-482",
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.25),
        logger=logger,
        metrics=metrics,
        sleep=delays.append,
        clock=lambda: next(clock_values),
    )

    assert result == DeliveryResult((migration.migration_id,), (), 2)
    assert delays == [0.25]
    assert shared.committed_commands == [(migration.commands[0].text, migration.commands[0].params)]
    assert factory.sessions[1].events == ["rollback", "close"]
    assert factory.sessions[2].events == ["commit", "close"]
    assert any(
        event == "migration.attempt_failed"
        and fields["request_id"] == "change-482"
        and fields["migration_id"] == migration.migration_id
        and fields["error_type"] == "RetryableDatabaseError"
        for event, fields in logger.events
    )
    assert all("request_id" not in tags for _, _, tags in metrics.counters)
    assert metrics.observations == [
        ("migration_duration_seconds", 0.75, {"migration_id": migration.migration_id})
    ]


def test_uncertain_commit_rechecks_metadata_and_does_not_repeat_commands() -> None:
    migration = sample_migration()
    shared = SharedDatabase(fail_migration_commit_once=True)
    factory = FakeSessionFactory(shared)

    result = deliver_migrations(
        factory,
        (migration,),
        request_id="change-uncertain",
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0),
        logger=EventCollector(),
        metrics=MetricCollector(),
        sleep=lambda _: None,
        clock=lambda: 0.0,
    )

    assert result == DeliveryResult((), (migration.migration_id,), 2)
    assert shared.applied == {migration.migration_id: migration.checksum}
    assert shared.committed_commands == [(migration.commands[0].text, migration.commands[0].params)]


def test_redacted_json_logs_never_emit_credentials(
    caplog: pytest.LogCaptureFixture,
) -> None:
    fields = {
        "request_id": "change-482",
        # secret-scan: allow-fixture
        "database_url": "postgresql://learner:very-secret@localhost/course",
        # secret-scan: allow-fixture
        "detail": "postgresql://learner:another-secret@localhost/course",
        "payload": {"private": "record"},
        "attempt": 1,
    }
    assert redact_fields(fields) == {
        "request_id": "change-482",
        "database_url": "[REDACTED]",
        "detail": "[REDACTED]",
        "payload": "[REDACTED]",
        "attempt": 1,
    }

    caplog.set_level(logging.INFO)
    JsonEventLogger().emit("migration.test", fields)
    assert "change-482" in caplog.text
    assert "very-secret" not in caplog.text
    assert "another-secret" not in caplog.text
    assert "private" not in caplog.text


def test_readiness_is_read_only_and_reports_drift() -> None:
    migration = sample_migration()
    shared = SharedDatabase(
        metadata_exists=True,
        applied={migration.migration_id: migration.checksum},
    )
    factory = FakeSessionFactory(shared)
    assert check_readiness(factory, (migration,)) == ReadinessResult(
        True,
        migration.migration_id,
        migration.migration_id,
        (),
    )
    assert factory.sessions[-1].events == ["rollback", "close"]

    shared.applied[migration.migration_id] = "drifted"
    drifted = check_readiness(factory, (migration,))
    assert drifted.ready is False
    assert drifted.reasons == (f"checksum drift detected for {migration.migration_id}",)

    missing = check_readiness(FakeSessionFactory(SharedDatabase()), (migration,))
    assert missing.ready is False
    assert missing.reasons == ("migration metadata is absent",)


def test_recovery_decisions_require_rehearsed_evidence() -> None:
    incomplete = RecoveryEvidence(False, True, True, True, True, True)
    assert decide_recovery(incomplete) is RecoveryDecision.PAUSE_AND_GATHER_EVIDENCE

    written = RecoveryEvidence(True, True, True, True, True, True)
    assert decide_recovery(written) is RecoveryDecision.FORWARD_FIX

    reversible = RecoveryEvidence(True, True, False, True, True, False)
    assert decide_recovery(reversible) is RecoveryDecision.ROLLBACK_RELEASE

    unrehearsed = RecoveryEvidence(True, True, False, False, False, False)
    assert decide_recovery(unrehearsed) is RecoveryDecision.PAUSE_AND_GATHER_EVIDENCE


def test_live_url_guard_reveals_no_secret_in_errors() -> None:
    safe = require_course_database_url(
        {
            "DS60_DATABASE_URL": (
                # secret-scan: allow-fixture
                "postgresql://learner:private-value@localhost:5432/advanced_sql_training"
            )
        }
    )
    assert safe.endswith("/advanced_sql_training")

    with pytest.raises(ValueError) as caught:
        require_course_database_url(
            {
                # secret-scan: allow-fixture
                "DS60_DATABASE_URL": "postgresql://learner:private-value@localhost/valuable",
            }
        )
    assert "private-value" not in str(caught.value)
