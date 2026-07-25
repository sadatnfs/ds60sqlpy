"""Day 8 reference: observable, resumable, security-conscious pipeline orchestration."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from urllib.parse import parse_qs, urlsplit


@dataclass(frozen=True)
class Record:
    sequence: int
    record_id: str
    amount: Decimal


@dataclass(frozen=True)
class JobResult:
    records_read: int
    records_written: int
    checkpoint: int | None


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
    """Coordinate effects while keeping recovery order explicit."""

    def __init__(
        self,
        *,
        job_name: str,
        extractor: Extractor,
        sink: Sink,
        checkpoints: CheckpointStore,
        metrics: Metrics,
        batch_size: int = 100,
        logger: logging.Logger | None = None,
    ) -> None:
        if not job_name.strip():
            raise ValueError("job_name cannot be blank")
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        self._job_name = job_name
        self._extractor = extractor
        self._sink = sink
        self._checkpoints = checkpoints
        self._metrics = metrics
        self._batch_size = batch_size
        self._logger = logger or logging.getLogger(__name__)

    def run_once(self) -> JobResult:
        """Resume after the durable checkpoint and advance it only after each write."""

        starting_checkpoint = self._checkpoints.load()
        records = list(self._extractor.extract_after(starting_checkpoint))
        self._validate_order(records, starting_checkpoint)
        tags = {"job": self._job_name}
        self._metrics.increment("records_read", len(records), tags=tags)
        current_checkpoint = starting_checkpoint
        written = 0

        try:
            for start in range(0, len(records), self._batch_size):
                batch = records[start : start + self._batch_size]
                self._sink.write(batch)
                current_checkpoint = batch[-1].sequence
                self._checkpoints.save(current_checkpoint)
                written += len(batch)
                self._metrics.increment("records_written", len(batch), tags=tags)
        except BaseException as exc:
            error_type = type(exc).__name__
            self._metrics.increment(
                "job_failures",
                tags={**tags, "error_type": error_type},
            )
            self._logger.error(
                "job failed job=%s records_written=%d error_type=%s",
                self._job_name,
                written,
                error_type,
            )
            raise

        self._metrics.increment("job_successes", tags=tags)
        self._logger.info(
            "job complete job=%s records_read=%d records_written=%d",
            self._job_name,
            len(records),
            written,
        )
        return JobResult(len(records), written, current_checkpoint)

    @staticmethod
    def _validate_order(records: Sequence[Record], checkpoint: int | None) -> None:
        previous = checkpoint
        seen_ids: set[str] = set()
        for record in records:
            if record.sequence < 1:
                raise ValueError("record sequence must be positive")
            if previous is not None and record.sequence <= previous:
                raise ValueError("records must be strictly ordered after the checkpoint")
            if not record.record_id or record.record_id in seen_ids:
                raise ValueError("record IDs must be non-empty and unique within a run")
            if not record.amount.is_finite() or record.amount <= 0:
                raise ValueError("record amount must be finite and positive")
            previous = record.sequence
            seen_ids.add(record.record_id)


def validate_database_transport(database_url: str) -> None:
    """Reject non-PostgreSQL URLs and insecure non-local connections."""

    parsed = urlsplit(database_url)
    if parsed.scheme not in {"postgresql", "postgres"} or not parsed.hostname:
        raise ValueError("DS60_DATABASE_URL must be a PostgreSQL URL")
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        return
    ssl_modes = parse_qs(parsed.query).get("sslmode", [])
    if not ssl_modes or ssl_modes[-1] not in {"require", "verify-ca", "verify-full"}:
        raise ValueError("remote PostgreSQL connections must require TLS")
