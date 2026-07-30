"""Bridge Day 6: bulk extract-transform-load work and validation.

Prerequisite: Bridge Day 5.
Read ``bridge/companion-guides/day06_bulk_etl_validation.md`` first.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol, TypeVar

LESSON_ID = "bridge-06"
PREREQUISITES = ("bridge-05",)
LEVEL = "advanced"

T = TypeVar("T")


class RowValidationError(ValueError):
    """One source row did not satisfy the input contract."""


@dataclass(frozen=True)
class Sale:
    source_id: str
    customer_id: int
    amount: Decimal
    occurred_on: date


@dataclass(frozen=True)
class RejectedRow:
    source_id: str
    reason: str


class BulkCursor(Protocol):
    def executemany(
        self,
        query: object,
        params_seq: Iterable[Sequence[object]],
    ) -> object: ...


def parse_sale(raw: Mapping[str, str]) -> Sale:
    """Core implementation: validate identifiers, numeric fields, and ISO dates."""

    raise NotImplementedError("convert one raw row or raise RowValidationError")


def partition_rows(
    rows: Iterable[Mapping[str, str]],
) -> tuple[list[Sale], list[RejectedRow]]:
    """Core implementation: retain valid rows and minimal diagnostics for rejected rows."""

    raise NotImplementedError("partition without logging complete source records")


def batches(items: Sequence[T], size: int) -> list[tuple[T, ...]]:
    """Core implementation: create deterministic batches and reject invalid sizes."""

    raise NotImplementedError("split a sequence into non-empty batches")


def load_sales(cursor: BulkCursor, sales: Sequence[Sale]) -> int:
    """Core implementation: use parameterized ``executemany`` or a Psycopg COPY path."""

    raise NotImplementedError("bulk-load already validated records")


# Exercises (answer-free)
# Focus: Validate untrusted rows before I/O, retain minimal rejection evidence, batch
#    deterministically, and submit typed parameters through an idempotent bulk boundary.
# Assumptions: Money is finite, positive, and quantized to two decimals; source IDs are stable
#    replay keys; raw records may contain sensitive fields.
# Failure to watch for: Bulk speed does not excuse weak validation, unbounded materialization,
#    or diagnostics that copy entire rejected records.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Validation] Implement `parse_sale()` for non-blank source ID, positive integer customer
#    ID, finite positive amount, and ISO date without mutating input.
#    Hint: Convert each field explicitly and translate only expected conversion failures.
# 2. [Money] Quantize accepted amounts to two decimals and document the chosen rounding rule.
#    Hint: Quantization is a domain decision, not merely display formatting.
# 3. [Partitioning] Implement `partition_rows()` so accepted sales and rejected source
#    IDs/reasons retain input order without storing full raw rows.
#    Hint: Catch only `RowValidationError` from the conversion boundary.
# 4. [Batching] Implement `batches()` with positive-size validation and tests for empty, exact,
#    and remainder cases.
#    Hint: Slice deterministic tuples from the original sequence.
# 5. [Bulk SQL] Implement a parameterized `executemany()` upsert into `pg_temp.bridge_sales`
#    with no values in SQL text.
#    Hint: Convert typed sales to one parameter tuple per row.
# 6. [Accounting] Track accepted, rejected, submitted, inserted, and updated counts separately
#    and state what `executemany()` cannot cheaply distinguish.
#    Hint: Do not infer business outcomes from submitted row count.
# 7. [Extension] Design the Psycopg COPY variant using typed `write_row()` calls and a staging
#    table instead of hand-built delimited text.
#    Hint: COPY handles transport; a later set-based statement owns merge semantics.
# 8. [Edge cases] Test NaN, infinities, zero, negatives, whitespace IDs, leading-zero customer
#    IDs, and invalid dates.
#    Hint: Classify each rejection at the field boundary and keep its reason safe.
# 9. [Idempotency] Choose a policy for duplicate `source_id` values within one input batch and
#    test it before database submission.
#    Hint: Database upsert resolves persisted conflicts but may hide contradictory source rows.
# 10. [Scale design] Compare materializing all accepted rows with a streaming validator and
#    identify where bounded memory changes APIs.
#    Hint: A tuple return is convenient for lessons but not for unlimited sources.
# 11. [Capacity] Select batch size from parameter count, row width, memory, and transaction
#    duration rather than a universal constant.
#    Hint: Measure the real adapter and keep a safe configurable default.
# 12. [Transaction failure] Specify behavior when `executemany()` fails halfway and identify
#    which layer owns rollback and retry.
#    Hint: Submission count is not committed count.
# 13. [Observability] Create a bounded rejection taxonomy and metrics that do not use source IDs
#    or raw reasons as tags.
#    Hint: Metric labels must come from a fixed vocabulary.
# 14. [Reconciliation] Design a replay test that loads the same accepted sales twice and
#    reconciles source IDs and total amount.
#    Hint: Idempotency is proven by stable final state, not by absence of exceptions.


def main() -> int:
    print("Bridge Day 6 starter loaded; it performs no I/O by default.")
    print("Validate, partition, batch, and load deterministic sales rows.")
    print("Track accepted, rejected, and submitted counts separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
