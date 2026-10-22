"""Independent fixture and fake-effect checks for the offline capstone."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from bridge.professional.solutions.bridge_capstone_01_evidence_review_solution import (
    FIXTURES,
    Difference,
    ProductRow,
    ReleaseRejected,
    SourceLine,
    Summary,
    build_product,
    canonical_digest,
    incident_review,
    load_product,
    load_source_lines,
    normalize,
    publish_checked,
    reconcile,
    summarize,
    write_evidence,
)

GOLDEN = (ProductRow("A", 10000), ProductRow("B", 5000), ProductRow("C", 0))
INCIDENT = (ProductRow("A", 10000), ProductRow("B", 4000), ProductRow("D", 1000))


@dataclass
class RecordingPublisher:
    calls: list[tuple[str, tuple[ProductRow, ...], str]] = field(default_factory=list)
    fail_after_recording: bool = False

    def publish(self, release_id: str, rows: tuple[ProductRow, ...], digest: str) -> None:
        self.calls.append((release_id, rows, digest))
        if self.fail_after_recording:
            raise RuntimeError("acknowledgement lost; outcome requires investigation")


def test_golden_is_independent_of_the_repair_transform() -> None:
    assert load_product(FIXTURES / "golden_product.json") == GOLDEN
    assert load_product(FIXTURES / "incident_product.json") == INCIDENT
    assert summarize(GOLDEN) == summarize(INCIDENT) == Summary(3, 15000)


@pytest.mark.parametrize(
    "raw",
    [
        {"invoice_id": "A", "amount_cents": 1},
        [{"invoice_id": "A", "amount_cents": True}],
        [{"invoice_id": "A", "amount_cents": -1}],
        [{"invoice_id": "A", "amount_cents": 1.0}],
        [{"invoice_id": " A", "amount_cents": 1}],
        [{"invoice_id": "", "amount_cents": 1}],
        [{"invoice_id": "A", "amount_cents": 1, "extra": "unexpected"}],
        [{"invoice_id": "A"}],
        [
            {"invoice_id": "A", "amount_cents": 1},
            {"invoice_id": "A", "amount_cents": 1},
        ],
    ],
)
def test_product_boundary_rejects_malformed_or_ambiguous_contracts(
    tmp_path: Path, raw: object
) -> None:
    source = tmp_path / "input.json"
    source.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError):
        load_product(source)


def test_keyed_comparison_finds_both_missing_directions_and_changed_value() -> None:
    evidence = reconcile(GOLDEN, INCIDENT)
    assert not evidence.accepted
    assert evidence.differences == (
        Difference("B", 5000, 4000, "changed"),
        Difference("C", 0, None, "missing"),
        Difference("D", None, 1000, "unexpected"),
    )
    assert evidence.expected_summary == evidence.actual_summary
    assert evidence.expected_digest != evidence.actual_digest
    assert reconcile((), ()).accepted
    assert reconcile((ProductRow("Z", 0),), ()).differences == (
        Difference("Z", 0, None, "missing"),
    )


def test_repair_preserves_zero_line_invoice_and_does_not_mutate_source() -> None:
    lines = list(load_source_lines(FIXTURES / "source_lines.json"))
    original = lines.copy()
    repaired = build_product(("C", "B", "A"), lines)
    assert repaired == GOLDEN
    assert lines == original
    assert reconcile(GOLDEN, repaired).accepted
    assert build_product((), ()) == ()
    assert build_product(("Z",), ()) == (ProductRow("Z", 0),)


@pytest.mark.parametrize(
    ("identities", "lines", "message"),
    [
        (("A", "A"), (), "duplicate invoice"),
        (("A",), (SourceLine("L1", "B", 1),), "absent from the manifest"),
        (("A",), (SourceLine("L1", "A", -1),), "nonnegative integer"),
        (("A",), (SourceLine("L1", "A", True),), "nonnegative integer"),
        (
            ("A",),
            (SourceLine("L1", "A", 1), SourceLine("L1", "A", 1)),
            "duplicate line_id",
        ),
    ],
)
def test_repair_refuses_inputs_that_would_hide_quality_defects(
    identities: tuple[str, ...], lines: tuple[SourceLine, ...], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        build_product(identities, lines)


def test_canonical_digest_is_order_independent_and_contract_sensitive() -> None:
    assert canonical_digest(GOLDEN) == canonical_digest(tuple(reversed(GOLDEN)))
    assert canonical_digest(GOLDEN) == (
        "fddc2c8909fee69e1b96661b9e11a1e87c7212bfe2d5f731a9f45ed2ae868fc3"
    )
    assert canonical_digest(GOLDEN) != canonical_digest(INCIDENT)
    with pytest.raises(ValueError, match="duplicate invoice_id"):
        canonical_digest((ProductRow("A", 1), ProductRow("A", 1)))


def test_publication_gate_rejects_incident_before_the_fake_effect() -> None:
    publisher = RecordingPublisher()
    with pytest.raises(ReleaseRejected):
        publish_checked("release-1", GOLDEN, INCIDENT, publisher)
    assert publisher.calls == []
    result = publish_checked("release-2", GOLDEN, tuple(reversed(GOLDEN)), publisher)
    assert result.accepted
    assert publisher.calls == [("release-2", GOLDEN, result.actual_digest)]


def test_publication_failure_is_not_retried_or_reported_as_success() -> None:
    publisher = RecordingPublisher(fail_after_recording=True)
    with pytest.raises(RuntimeError, match="acknowledgement lost"):
        publish_checked("release-unknown", GOLDEN, GOLDEN, publisher)
    assert len(publisher.calls) == 1


def test_publication_uses_a_frozen_reviewed_snapshot() -> None:
    incoming = list(reversed(GOLDEN))

    class MutatingCallerPublisher:
        observed: tuple[ProductRow, ...] = ()

        def publish(self, release_id: str, rows: tuple[ProductRow, ...], digest: str) -> None:
            incoming.clear()
            self.observed = rows

    publisher = MutatingCallerPublisher()
    publish_checked("release-frozen", GOLDEN, incoming, publisher)
    assert incoming == []
    assert publisher.observed == GOLDEN


def test_evidence_round_trips_and_preserves_existing_work(tmp_path: Path) -> None:
    evidence = reconcile(GOLDEN, INCIDENT)
    report = tmp_path / "review.json"
    write_evidence(evidence, report)
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["contract_version"] == 1
    assert payload["accepted"] is False
    assert payload["differences"][1] == {
        "invoice_id": "C",
        "expected_cents": 0,
        "actual_cents": None,
        "kind": "missing",
    }
    assert payload["expected_digest"] == canonical_digest(GOLDEN)
    original = report.read_bytes()
    with pytest.raises(FileExistsError):
        write_evidence(reconcile(GOLDEN, GOLDEN), report)
    assert report.read_bytes() == original


def test_incident_review_bounds_claims_and_keeps_the_golden_contract() -> None:
    rejected = reconcile(GOLDEN, INCIDENT)
    accepted = reconcile(GOLDEN, GOLDEN)
    note = incident_review(rejected, accepted)
    assert "matching row count and total cents" in note.observed
    assert "B: changed" in note.impact
    assert "C: missing" in note.impact
    assert note.cause_status.startswith("Unproven:")
    assert any("production recovery" in item for item in note.unresolved)
    with pytest.raises(ValueError, match="rejected before"):
        incident_review(accepted, accepted)
    with pytest.raises(ValueError, match="rejected before"):
        incident_review(rejected, rejected)
    different_golden = (ProductRow("Z", 1),)
    with pytest.raises(ValueError, match="same independent golden"):
        incident_review(rejected, reconcile(different_golden, different_golden))


def test_normalization_never_hides_duplicate_identities() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        normalize((ProductRow("A", 1), ProductRow("A", 2)))
