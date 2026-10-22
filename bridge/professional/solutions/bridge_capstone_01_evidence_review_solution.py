"""Offline data-product review with independent golden evidence and fake effects."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

LESSON_ID = "bridge-capstone-01"
PREREQUISITES = ("bridge-08", "sql-quality-01", "python-pro-03")
LEVEL = "advanced"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "capstone"


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
        return not self.differences


@dataclass(frozen=True)
class IncidentReview:
    observed: str
    impact: str
    cause_status: str
    repair: str
    verification: str
    unresolved: tuple[str, ...]


class Publisher(Protocol):
    """Caller-owned side effect; failures propagate without an automatic retry."""

    def publish(self, release_id: str, rows: tuple[ProductRow, ...], digest: str) -> None: ...


class ReleaseRejected(ValueError):
    """Data failed the declared independent golden contract before publication."""


def _identity(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty text without outer whitespace")
    return value


def _amount(value: object) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("amount_cents must be a nonnegative integer, excluding bool")
    return value


def normalize(rows: Sequence[ProductRow]) -> tuple[ProductRow, ...]:
    """Validate the keyed contract before sorting or comparing attributes."""
    identities: set[str] = set()
    for row in rows:
        _identity(row.invoice_id, "invoice_id")
        _amount(row.amount_cents)
        if row.invoice_id in identities:
            raise ValueError("duplicate invoice_id")
        identities.add(row.invoice_id)
    return tuple(sorted(rows, key=lambda row: row.invoice_id))


def load_product(path: Path) -> tuple[ProductRow, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("product JSON must be a list")
    rows: list[ProductRow] = []
    for item in raw:
        if not isinstance(item, dict) or set(item) != {"invoice_id", "amount_cents"}:
            raise ValueError("product row must contain exactly invoice_id and amount_cents")
        rows.append(
            ProductRow(_identity(item["invoice_id"], "invoice_id"), _amount(item["amount_cents"]))
        )
    return normalize(rows)


def load_source_lines(path: Path) -> tuple[SourceLine, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("source JSON must be a list")
    rows: list[SourceLine] = []
    for item in raw:
        if not isinstance(item, dict) or set(item) != {"line_id", "invoice_id", "amount_cents"}:
            raise ValueError("source row has unexpected fields")
        rows.append(
            SourceLine(
                _identity(item["line_id"], "line_id"),
                _identity(item["invoice_id"], "invoice_id"),
                _amount(item["amount_cents"]),
            )
        )
    return tuple(rows)


def summarize(rows: Sequence[ProductRow]) -> Summary:
    checked = normalize(rows)
    return Summary(len(checked), sum(row.amount_cents for row in checked))


def canonical_digest(rows: Sequence[ProductRow]) -> str:
    payload = {"contract_version": 1, "rows": [asdict(row) for row in normalize(rows)]}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def reconcile(expected: Sequence[ProductRow], actual: Sequence[ProductRow]) -> Evidence:
    expected_rows, actual_rows = normalize(expected), normalize(actual)
    left = {row.invoice_id: row.amount_cents for row in expected_rows}
    right = {row.invoice_id: row.amount_cents for row in actual_rows}
    differences: list[Difference] = []
    for invoice_id in sorted(left.keys() | right.keys()):
        if invoice_id not in left:
            kind = "unexpected"
        elif invoice_id not in right:
            kind = "missing"
        elif left[invoice_id] != right[invoice_id]:
            kind = "changed"
        else:
            continue
        differences.append(
            Difference(invoice_id, left.get(invoice_id), right.get(invoice_id), kind)
        )
    return Evidence(
        summarize(expected_rows),
        summarize(actual_rows),
        canonical_digest(expected_rows),
        canonical_digest(actual_rows),
        tuple(differences),
    )


def build_product(
    invoice_ids: Sequence[str], lines: Sequence[SourceLine]
) -> tuple[ProductRow, ...]:
    """Aggregate validated source lines while preserving zero-line invoices."""
    totals: dict[str, int] = {}
    for invoice_id in invoice_ids:
        checked = _identity(invoice_id, "invoice_id")
        if checked in totals:
            raise ValueError("duplicate invoice identity in manifest")
        totals[checked] = 0
    seen: set[str] = set()
    for line in lines:
        line_id = _identity(line.line_id, "line_id")
        if line_id in seen:
            raise ValueError("duplicate line_id")
        seen.add(line_id)
        invoice_id = _identity(line.invoice_id, "invoice_id")
        if invoice_id not in totals:
            raise ValueError("line references an invoice absent from the manifest")
        totals[invoice_id] += _amount(line.amount_cents)
    return normalize([ProductRow(invoice_id, amount) for invoice_id, amount in totals.items()])


def publish_checked(
    release_id: str,
    expected: Sequence[ProductRow],
    actual: Sequence[ProductRow],
    publisher: Publisher,
) -> Evidence:
    checked_id = _identity(release_id, "release_id")
    # Snapshot caller input once so the reviewed data and emitted data agree.
    rows = normalize(actual)
    evidence = reconcile(expected, rows)
    if not evidence.accepted:
        raise ReleaseRejected("invoice identities or amounts differ from the golden contract")
    publisher.publish(checked_id, rows, evidence.actual_digest)
    return evidence


def write_evidence(evidence: Evidence, path: Path) -> None:
    """Create a deterministic review artifact without overwriting existing work."""
    payload = {"contract_version": 1, "accepted": evidence.accepted, **asdict(evidence)}
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(payload, output, sort_keys=True, indent=2, ensure_ascii=True)
        output.write("\n")


def incident_review(before: Evidence, after: Evidence) -> IncidentReview:
    if before.accepted or not after.accepted:
        raise ValueError("review requires rejected before evidence and accepted repair evidence")
    if before.expected_digest != after.expected_digest:
        raise ValueError("repair must use the same independent golden contract")
    summary_note = (
        "matching row count and total cents"
        if before.expected_summary == before.actual_summary
        else "different summary controls"
    )
    impact = "; ".join(
        f"{difference.invoice_id}: {difference.kind}, "
        f"expected_cents={difference.expected_cents}, actual_cents={difference.actual_cents}"
        for difference in before.differences
    )
    return IncidentReview(
        observed=f"{len(before.differences)} keyed differences exist alongside {summary_note}.",
        impact=impact,
        cause_status=(
            "Unproven: the supplied snapshots do not identify the historical defect or actor."
        ),
        repair="Rebuild from validated source lines and the complete invoice manifest.",
        verification=(
            "The repaired keyed relation matches the unchanged independent golden fixture."
        ),
        unresolved=(
            "Whether a real consumer received the incident release is unknown.",
            "The original transform and deployment timeline are not supplied.",
            "Fake publication evidence does not prove production recovery.",
        ),
    )


def main() -> None:
    golden = load_product(FIXTURES / "golden_product.json")
    broken = load_product(FIXTURES / "incident_product.json")
    before = reconcile(golden, broken)
    repaired = build_product(("A", "B", "C"), load_source_lines(FIXTURES / "source_lines.json"))
    after = reconcile(golden, repaired)
    print(
        json.dumps(
            {
                "incident": {"accepted": before.accepted, **asdict(before)},
                "repair": {"accepted": after.accepted, **asdict(after)},
                "review": asdict(incident_review(before, after)),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
