"""Guard complete browser inventory and read-only original-observation persistence."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

import pytest

from scripts import check_plotly_browser as gate
from scripts.check_d3_browser import validate_observation
from scripts.check_scientific_artifacts import pad_digest

ROOT = Path(__file__).resolve().parents[1]
BrowserFixture = tuple[
    dict[str, dict[str, Any]], dict[str, dict[str, str]], dict[str, Any], dict[str, Any]
]


def observation(row: dict[str, Any], number: int) -> dict[str, Any]:
    return {
        "kind": "browser_observation",
        "lesson_id": row["id"],
        "profile": "javascript-browser",
        "language": "javascript",
        "library": "d3@7.9.0+plotly@4.1.2",
        "verification_kind": "browser_observation",
        "verified": False,
        "checks": [],
        "returncode": None,
        "status": "succeeded",
        "source": row["source"],
        "source_sha256": hashlib.sha256(row["source"].encode()).hexdigest(),
        "output": row["marker"],
        "job_id": f"{number:032x}",
    }


def test_every_admitted_plotly_browser_variant_has_a_bounded_reference() -> None:
    rows = gate.references(ROOT)
    assert tuple(row["id"] for row in rows) == gate.IDS
    assert [row["expected_table_rows"] for row in rows] == [3, 4, 3, 8, 3, 8, 3, 3]
    assert all(row["marker"] in row["source"] for row in rows)


@pytest.fixture
def fixture() -> BrowserFixture:
    rows = gate.references(ROOT)
    records = {row["id"]: observation(row, n) for n, row in enumerate(rows, 1)}
    sessions = {
        identity: {"source": "# retained " + identity, "explanation": "retained note"}
        for identity in (*gate.IDS, gate.DAX_ID)
    }
    dax: dict[str, Any] = {
        "lesson_id": gate.DAX_ID,
        "evidence": "hand-derived",
        "executed": False,
        "reference_source": 'EVALUATE ROW("x",1)',
        "cases": [{"rows": [[1]]}],
        "source_sha256": "a" * 64,
        "model_sha256": "b" * 64,
    }
    report: dict[str, Any] = {
        "passed": True,
        "references": [
            validate_observation(records[row["id"]], row["id"], row["source"], row["marker"])
            for row in rows
        ],
        "pads": [
            {"lesson_id": identity, "sha256": pad_digest(sessions[identity])}
            for identity in (*gate.IDS, gate.DAX_ID)
        ],
        "dax": {"reference_sha256": gate.validate_dax_reference(dax)},
    }
    return records, sessions, dax, report


class Client:
    def __init__(self, fixture: BrowserFixture) -> None:
        self.records, self.sessions, self.dax, self.report = copy.deepcopy(fixture)
        self.actions: list[str] = []

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append(action)
        if action == "module-browser-result":
            record = self.records[fields["lesson_id"]]
            assert fields["receipt_id"] == record["job_id"]
            return {"receipt": record}
        if action == "module-lesson":
            return {"session": self.sessions[fields["lesson_id"]]}
        if action == "module-worked-examples":
            assert fields == {"lesson_id": gate.DAX_ID, "reveal": True}
            return self.dax
        raise AssertionError("Persistence attempted a write or execution: " + action)


def test_persistence_reads_exact_original_ids_and_drafts_without_playwright(
    fixture: BrowserFixture,
) -> None:
    client = Client(fixture)
    result = gate.verify_persistence(client, client.report)
    assert result["passed"] and result["observations"] == 8 and result["pads"] == 9
    assert client.actions.count("module-browser-result") == 8
    assert client.actions.count("module-lesson") == 9
    assert set(client.actions) == {
        "module-browser-result",
        "module-lesson",
        "module-worked-examples",
    }


@pytest.mark.parametrize("change", ["observation", "draft", "dax_reference", "missing_case"])
def test_changed_or_incomplete_evidence_cannot_pass_persistence(
    fixture: BrowserFixture, change: str
) -> None:
    client = Client(fixture)
    if change == "observation":
        client.records[gate.IDS[0]]["output"] += "\nchanged"
    elif change == "draft":
        client.sessions[gate.DAX_ID]["source"] = "replaced"
    elif change == "dax_reference":
        client.dax["model_sha256"] = "c" * 64
    else:
        client.report["references"].pop()
    with pytest.raises(ValueError):
        gate.verify_persistence(client, client.report)
    assert not {"module-run", "module-save", "module-browser-record"} & set(client.actions)


@pytest.mark.parametrize(
    "update",
    [{"executed": True}, {"evidence": "runtime"}, {"source_sha256": "missing"}, {"cases": []}],
)
def test_dax_reference_cannot_be_reclassified_as_execution(
    fixture: BrowserFixture, update: dict[str, Any]
) -> None:
    dax = {**fixture[2], **update}
    with pytest.raises(ValueError):
        gate.validate_dax_reference(dax)
