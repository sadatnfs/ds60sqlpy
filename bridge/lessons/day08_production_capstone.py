"""Bridge Day 8: observable, secure, failure-aware production capstone.

Prerequisite: Bridge Day 7.
Read ``bridge/companion-guides/day08_production_capstone.md`` first.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

LESSON_ID = "bridge-08"
PREREQUISITES = ("bridge-07",)
LEVEL = "advanced"


@dataclass(frozen=True)
class Record:
    sequence: int
    record_id: str
    amount: Decimal


class Extractor(Protocol):
    def extract_after(self, checkpoint: int | None) -> Sequence[Record]: ...


class Sink(Protocol):
    def write(self, records: Sequence[Record]) -> None: ...


class CheckpointStore(Protocol):
    def load(self) -> int | None: ...

    def save(self, checkpoint: int) -> None: ...


class Metrics(Protocol):
    def increment(
        self,
        name: str,
        value: int = 1,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None: ...


class JobRunner:
    """Core implementation: orchestrate effects with a recoverable checkpoint order."""

    def __init__(
        self,
        *,
        extractor: Extractor,
        sink: Sink,
        checkpoints: CheckpointStore,
        metrics: Metrics,
        batch_size: int,
    ) -> None:
        raise NotImplementedError("validate and retain injected dependencies")

    def run_once(self) -> object:
        raise NotImplementedError("write each batch before advancing its checkpoint")


def validate_database_transport(database_url: str) -> None:
    """Core implementation: require PostgreSQL and transport security for remote hosts."""

    raise NotImplementedError("validate without printing or returning the secret URL")


# Exercises (answer-free)
# Focus: Orchestrate a restart-safe batch job through injected effects, validation-before-write,
#    post-write checkpoints, bounded observability, and safe database transport.
# Assumptions: Records have strictly increasing positive sequences and finite positive Decimal
#    amounts; a checkpoint advances only after its batch write succeeds.
# Failure to watch for: An advanced checkpoint or non-idempotent ambiguous sink write can
#    permanently skip or duplicate records during recovery.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Validation] Validate constructor inputs, including non-blank job name and positive batch
#    size, before retaining dependencies.
#    Hint: Reject invalid orchestration configuration before the first effect.
# 2. [Orchestration] Implement `run_once()` in load-extract-validate-batch-write-checkpoint
#    order and return read, written, and final checkpoint evidence.
#    Hint: Validate the full extracted sequence before the first sink call.
# 3. [Test doubles] Build extractor, sink, checkpoint, and metric fakes; configure the sink to
#    fail on a selected call.
#    Hint: Fakes should expose histories and deterministic failure switches.
# 4. [Recovery test] With four records and batch size two, fail write two, assert only
#    checkpoint two persists, then resume from two with a healthy sink.
#    Hint: Extraction on retry must receive the last durable checkpoint.
# 5. [Record validation] Reject duplicate IDs, non-positive/non-increasing sequences, and
#    non-finite/non-positive money before any sink effect.
#    Hint: Check global order/uniqueness after validating individual records.
# 6. [Observability] Emit success/failure and record-count metrics with only job and
#    exception-class tags.
#    Hint: Keep messages, record IDs, checkpoints, and request IDs out of metric dimensions.
# 7. [Transport security] Implement `validate_database_transport()` for PostgreSQL schemes,
#    local course hosts, and required TLS modes on remote hosts.
#    Hint: Parse without echoing; local and remote host policies differ.
# 8. [Runbook] Write operational steps for startup, health evidence, retry ownership, checkpoint
#    inspection, replay, rollback, credential rotation, and escalation.
#    Hint: Every action needs prerequisites, expected evidence, and a stop condition.
# 9. [No-op behavior] Define the result and metrics when extraction returns no records.
#    Hint: A no-op should not write or advance a checkpoint.
# 10. [Checkpoint validation] Detect records at or below the loaded checkpoint and out-of-order
#    extractor results before writing.
#    Hint: Do not assume an injected extractor obeys its Protocol's semantic promise.
# 11. [Ambiguous writes] Explain recovery when the sink commits a batch but the client raises
#    before seeing success.
#    Hint: Post-write checkpoint ordering alone cannot prevent a duplicate replay.
# 12. [Metric design] Classify which fields belong in metrics, structured logs, or neither, and
#    test cardinality.
#    Hint: Observability channels have different retention and indexing costs.
# 13. [Health model] Separate process liveness, dependency readiness, and last-run success for
#    the job.
#    Hint: A process can be alive while unable to make safe progress.
# 14. [URL edge cases] Test loopback names, IPv4/IPv6, missing host, case-insensitive TLS
#    values, unsupported schemes, and remote insecure modes.
#    Hint: Normalize parsed components and keep every failure message secret-free.
# 15. [Operations drill] Simulate credential rotation and prove the runner can restart without
#    resetting a valid checkpoint.
#    Hint: Credentials identify access, not processing position.
# 16. [Invariant testing] Generate failure positions across multiple batch sizes and prove
#    persisted checkpoints always correspond to fully successful batches.
#    Hint: Vary boundaries while holding deterministic records and fakes.


def main() -> int:
    print("Bridge Day 8 capstone starter loaded.")
    print("Build the runner from small fakes before adding an optional Psycopg adapter.")
    print("Prove restart safety by failing a batch and resuming from the last checkpoint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
