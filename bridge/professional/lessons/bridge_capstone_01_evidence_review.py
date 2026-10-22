"""BRIDGE-CAPSTONE-01: review an incident data product using independent evidence.

Read the guide first. Default execution is offline and answer-free. Implement
one contract at a time in your learner copy; main never calls an unfinished
function. The supplied JSON fixtures are synthetic, small, and immutable.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

LESSON_ID = "bridge-capstone-01"
PREREQUISITES = ("bridge-08", "sql-quality-01", "python-pro-03")
LEVEL = "advanced"
FIXTURES = Path("bridge/professional/fixtures/capstone")


@dataclass(frozen=True)
class ProductRow:
    invoice_id: str
    amount_cents: int


@dataclass(frozen=True)
class SourceLine:
    line_id: str
    invoice_id: str
    amount_cents: int


@dataclass(frozen=True)
class Summary:
    row_count: int
    amount_total_cents: int


@dataclass(frozen=True)
class Difference:
    invoice_id: str
    expected_cents: int | None
    actual_cents: int | None
    kind: str


@dataclass(frozen=True)
class Evidence:
    expected_summary: Summary
    actual_summary: Summary
    expected_digest: str
    actual_digest: str
    differences: tuple[Difference, ...]

    @property
    def accepted(self) -> bool:
        raise NotImplementedError("Complete the keyed evidence contract")


@dataclass(frozen=True)
class IncidentReview:
    observed: str
    impact: str
    cause_status: str
    repair: str
    verification: str
    unresolved: tuple[str, ...]


class Publisher(Protocol):
    def publish(self, release_id: str, rows: tuple[ProductRow, ...], digest: str) -> None: ...


class ReleaseRejected(ValueError):
    """The data failed the golden contract before publication was attempted."""


def normalize(rows: Sequence[ProductRow]) -> tuple[ProductRow, ...]:
    """Validate keys and integer cents, rejecting duplicate identities."""
    raise NotImplementedError("Exercise 1: validate the keyed product boundary")


def load_product(path: Path) -> tuple[ProductRow, ...]:
    raise NotImplementedError("Exercise 1: load and validate an exact JSON contract")


def summarize(rows: Sequence[ProductRow]) -> Summary:
    raise NotImplementedError("Exercise 2: retain useful but insufficient controls")


def reconcile(expected: Sequence[ProductRow], actual: Sequence[ProductRow]) -> Evidence:
    raise NotImplementedError("Exercise 3: compare identities and amounts in both directions")


def load_source_lines(path: Path) -> tuple[SourceLine, ...]:
    raise NotImplementedError("Exercise 4: parse supplied independent source facts")


def build_product(
    invoice_ids: Sequence[str], lines: Sequence[SourceLine]
) -> tuple[ProductRow, ...]:
    raise NotImplementedError("Exercise 4: preserve complete invoice identity and reject bad lines")


def canonical_digest(rows: Sequence[ProductRow]) -> str:
    raise NotImplementedError("Exercise 5: fingerprint a canonical typed contract")


def publish_checked(
    release_id: str,
    expected: Sequence[ProductRow],
    actual: Sequence[ProductRow],
    publisher: Publisher,
) -> Evidence:
    raise NotImplementedError("Exercise 6: gate the injected effect on exact evidence")


def write_evidence(evidence: Evidence, path: Path) -> None:
    raise NotImplementedError("Exercise 7: create a review artifact without overwriting work")


def incident_review(before: Evidence, after: Evidence) -> IncidentReview:
    raise NotImplementedError("Exercise 8: distinguish observed repair from unknown incident cause")


# Exercises
# 1. Load the product boundary. Validate exact fields, unique nonblank invoice_id,
#    and nonnegative integer cents, excluding bool. Retain zero-valued invoice C.
#    Expected: golden IDs A,B,C; malformed, bool, negative, and duplicate inputs raise ValueError.
# 2. Retain weak controls. Summarize golden_product.json and incident_product.json.
#    Expected: both Summary(3,15000), despite three keyed discrepancies.
# 3. Reconcile both directions. Return deterministic changed/missing/unexpected diagnostics.
#    Expected: B changed 5000 -> 4000, C missing 0 -> None, D unexpected None -> 1000.
# 4. Rebuild from source facts and complete manifest A,B,C. Reject duplicate line IDs and orphans.
#    Expected: A=10000,B=5000,C=0; three rows, same golden contract, no input mutation.
# 5. Canonicalize a versioned fingerprint. Sort by invoice identity before deterministic JSON
#    hashing.
#    Expected: row reordering preserves a 64-hex SHA-256 digest; changed amounts alter it.
# 6. Gate fake publication. Snapshot actual rows, compare, call Publisher only for exact matches.
#    Expected: zero fake calls for incident input, one for repaired input, no automatic retry on
#    error.
# 7. Write local evidence to a caller-supplied path with exclusive creation.
#    Expected: contract_version, accepted, summaries, digests and differences round-trip; existing
#    bytes survive.
# 8. Write an incident review with observations, impact, causal uncertainty, repair, and remaining
#    unknowns.
#    Expected: rejected-before/accepted-after use the same golden digest; no claim of production
#    recovery.


def main() -> None:
    print(f"{LESSON_ID}: synthetic fixtures are in {FIXTURES}")
    print(
        "Read the guide, predict the incident differences, then implement one exercise at a time."
    )
    print("No database, publication, file output, or network action is performed by this starter.")


if __name__ == "__main__":
    main()
