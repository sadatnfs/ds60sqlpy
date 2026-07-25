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
    """Exercise 1: orchestrate effects with a recoverable checkpoint order."""

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
    """Exercise 2: require PostgreSQL and transport security for remote hosts."""

    raise NotImplementedError("validate without printing or returning the secret URL")


def main() -> int:
    print("Bridge Day 8 capstone starter loaded.")
    print("Build the runner from small fakes before adding an optional Psycopg adapter.")
    print("Prove restart safety by failing a batch and resuming from the last checkpoint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
