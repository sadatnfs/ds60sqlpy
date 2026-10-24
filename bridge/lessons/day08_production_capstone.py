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
#    Verify: Construct runners with blank names and non-positive batch sizes; assert
#    `ValueError` before any dependency is retained or called, while a valid constructor has
#    zero effects.
# 2. [Orchestration] Implement `run_once()` in load-extract-validate-batch-write-checkpoint
#    order and return read, written, and final checkpoint evidence.
#    Hint: Validate the full extracted sequence before the first sink call.
#    Verify: For a two-batch run, assert event order `load, extract, validate, write,
#    checkpoint` per batch and compare `JobResult` read/written counts plus final checkpoint.
# 3. [Test doubles] Build extractor, sink, checkpoint, and metric fakes; configure the sink to
#    fail on a selected call.
#    Hint: Fakes should expose histories and deterministic failure switches.
#    Verify: Configure fakes with public call lists and sink failure index; assert inputs,
#    batches, checkpoint saves, metric events, and failure call are all independently
#    inspectable.
# 4. [Recovery test] With four records and batch size two, fail write two, assert only
#    checkpoint two persists, then resume from two with a healthy sink.
#    Hint: Extraction on retry must receive the last durable checkpoint.
#    Verify: With sequences 1–4 and batch size two, fail write two; assert checkpoint `2`, then
#    restart and assert only sequences 3–4 are written and checkpoint becomes `4`.
# 5. [Record validation] Reject duplicate IDs, non-positive/non-increasing sequences, and
#    non-finite/non-positive money before any sink effect.
#    Hint: Check global order/uniqueness after validating individual records.
#    Verify: Parameterize duplicate IDs, sequence zero, repeated/decreasing sequence,
#    `NaN`/infinity, and non-positive amount; assert each fails before the sink or checkpoint is
#    touched.
# 6. [Observability] Emit success/failure and record-count metrics with only job and
#    exception-class tags.
#    Hint: Keep messages, record IDs, checkpoints, and request IDs out of metric dimensions.
#    Verify: Inspect metrics/logs for success and failure: tags contain only
#    job/outcome/exception class, counts are correct, and records, URLs, and exception messages
#    are absent.
# 7. [Transport security] Implement `validate_database_transport()` for PostgreSQL schemes,
#    local course hosts, and required TLS modes on remote hosts.
#    Hint: Parse without echoing; local and remote host policies differ.
#    Verify: Accept local PostgreSQL URLs and remote URLs with `require`, `verify-ca`, or
#    `verify-full`; reject missing host, wrong scheme, and insecure remote mode without echoing
#    URL.
# 8. [Runbook] Write operational steps for startup, health evidence, retry ownership, checkpoint
#    inspection, replay, rollback, credential rotation, and escalation.
#    Hint: Every action needs prerequisites, expected evidence, and a stop condition.
#    Verify: Produce a runbook checklist covering startup, liveness/readiness/last-run evidence,
#    retry owner, checkpoint query, replay, rollback, rotation, escalation owner, and stop
#    condition.
# 9. [No-op behavior] Define the result and metrics when extraction returns no records.
#    Hint: A no-op should not write or advance a checkpoint.
#    Verify: For empty extraction, assert zero read/written counts, unchanged checkpoint, no
#    sink or checkpoint-save call, and one bounded successful no-op metric/event.
# 10. [Checkpoint validation] Detect records at or below the loaded checkpoint and out-of-order
#    extractor results before writing.
#    Hint: Do not assume an injected extractor obeys its Protocol's semantic promise.
#    Verify: Feed a record equal to the checkpoint and a decreasing pair; assert each raises
#    before the first write and leaves the stored checkpoint unchanged.
# 11. [Ambiguous writes] Explain recovery when the sink commits a batch but the client raises
#    before seeing success.
#    Hint: Post-write checkpoint ordering alone cannot prevent a duplicate replay.
#    Verify: Model server commit followed by client error; assert restart consults sink
#    idempotency evidence and checkpoint state before replaying rather than advancing blindly.
# 12. [Metric design] Classify which fields belong in metrics, structured logs, or neither, and
#    test cardinality.
#    Hint: Observability channels have different retention and indexing costs.
#    Verify: Classify job/outcome/error class/counts as bounded metrics, run/request ID as
#    structured log fields, and record IDs/payloads/URLs as neither; test the resulting
#    cardinality.
# 13. [Health model] Separate process liveness, dependency readiness, and last-run success for
#    the job.
#    Hint: A process can be alive while unable to make safe progress.
#    Verify: Return independent evidence for process liveness, dependency readiness, and
#    last-run success; force each one false while the other two remain true.
# 14. [URL edge cases] Test loopback names, IPv4/IPv6, missing host, case-insensitive TLS
#    values, unsupported schemes, and remote insecure modes.
#    Hint: Normalize parsed components and keep every failure message secret-free.
#    Verify: Parameterize localhost, loopback IPv4/IPv6, missing host, mixed-case TLS values,
#    wrong schemes, and insecure remote URLs; compare exact accept/reject outcomes and safe
#    messages.
# 15. [Operations drill] Simulate credential rotation and prove the runner can restart without
#    resetting a valid checkpoint.
#    Hint: Credentials identify access, not processing position.
#    Verify: Swap a secret-bearing URL between runs without changing checkpoint storage; assert
#    the new adapter is used, no URL is logged, and processing resumes after the valid
#    checkpoint.
# 16. [Invariant testing] Generate failure positions across multiple batch sizes and prove
#    persisted checkpoints always correspond to fully successful batches.
#    Hint: Vary boundaries while holding deterministic records and fakes.
#    Verify: Generate batch sizes and failure positions; after every failed run, assert
#    persisted checkpoint equals the last sequence of a fully completed batch and never a failed
#    batch.


def main() -> int:
    print("Bridge Day 8 capstone starter loaded.")
    print("Build the runner from small fakes before adding an optional Psycopg adapter.")
    print("Prove restart safety by failing a batch and resuming from the last checkpoint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
