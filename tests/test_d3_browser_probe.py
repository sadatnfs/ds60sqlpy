"""Protect source binding and honest browser-observation qualification."""

from __future__ import annotations

import hashlib
import importlib
from typing import Any

import pytest

from scripts import check_d3_browser as probe
from scripts.check_classroom_profiles import ClassroomClient


def observation() -> dict[str, Any]:
    source = "console.log('marker');\n"
    return {
        "kind": "browser_observation",
        "job_id": "a" * 32,
        "lesson_id": "js-043",
        "profile": "javascript-browser",
        "language": "javascript",
        "library": "d3@7.9.0",
        "verification_kind": "browser_observation",
        "verified": False,
        "checks": [],
        "returncode": None,
        "status": "succeeded",
        "source": source,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "output": "marker\n",
    }


def test_all_d3_references_match_their_browser_catalog_and_stable_markers() -> None:
    rows = probe.references()
    assert tuple(row["id"] for row in rows) == probe.IDS
    assert len(rows) == 24
    assert all(row["path"].endswith("_solution.js") for row in rows)
    assert all(row["marker"] in row["source"] for row in rows)


def test_saved_browser_observation_is_explicitly_untrusted() -> None:
    record = observation()
    result = probe.validate_observation(record, "js-043", record["source"], "marker")
    assert result["verified"] is False
    assert result["verification_kind"] == "browser_observation"
    assert "source" not in result and "output" not in result


@pytest.mark.parametrize(
    "change",
    [
        {"kind": "worker_job"},
        {"lesson_id": "js-044"},
        {"profile": "javascript-node"},
        {"language": "typescript"},
        {"library": "d3@unreviewed"},
        {"verification_kind": "typed_contract"},
        {"verified": True},
        {"checks": [{"passed": True}]},
        {"returncode": 0},
        {"status": "failed"},
        {"source": "different"},
        {"source_sha256": "different"},
        {"output": "no expected observation"},
        {"job_id": "not-an-observation-id"},
    ],
)
def test_qualification_rejects_misbound_or_overstated_evidence(change: dict[str, Any]) -> None:
    record = observation()
    with pytest.raises(ValueError, match="source, lesson or honest evidence"):
        probe.validate_observation({**record, **change}, "js-043", record["source"], "marker")


def test_failed_observation_requires_the_actual_failure_contract() -> None:
    record = {**observation(), "status": "failed", "output": "controlled failure"}
    result = probe.validate_observation(
        record, "js-043", record["source"], "controlled failure", "failed"
    )
    assert result["status"] == "failed" and result["verified"] is False


def test_disposable_authorization_precedes_browser_import_or_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda name: pytest.fail("browser import before authorization"),
    )
    with pytest.raises(SystemExit) as error:
        probe.main(["--url", "http://127.0.0.1:8765/classroom", "--report", "unused.json"])
    assert error.value.code == 2


class PersistenceClient(ClassroomClient):
    def __init__(self) -> None:
        self.actions: list[str] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.sessions: dict[str, dict[str, str]] = {}
        self.report: dict[str, Any] = {"passed": True, "references": [], "pads": []}
        for number, row in enumerate(probe.references(), 1):
            record = {
                **observation(),
                "job_id": f"{number:032x}",
                "lesson_id": row["id"],
                "source": row["source"],
                "source_sha256": hashlib.sha256(row["source"].encode()).hexdigest(),
                "output": row["marker"],
            }
            self.records[row["id"]] = record
            self.sessions[row["id"]] = {"source": row["source"], "explanation": "retained note"}
            self.report["references"].append(
                probe.validate_observation(record, row["id"], row["source"], row["marker"])
            )
            self.report["pads"].append(probe.pad_fingerprint(row["id"], self.sessions[row["id"]]))

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append(action)
        if action == "module-browser-result":
            record = self.records[fields["lesson_id"]]
            assert fields["receipt_id"] == record["job_id"]
            return {"receipt": record}
        if action == "module-lesson":
            return {"session": self.sessions[fields["lesson_id"]]}
        raise AssertionError("Persistence attempted a write or execution action: " + action)


def test_replacement_readback_preserves_original_evidence_and_never_executes() -> None:
    import copy

    client = PersistenceClient()
    original = copy.deepcopy(client.report)
    result = probe.verify_persistence(client, client.report)
    assert result["passed"] is True and result["observations"] == result["pads"] == 24
    assert client.report == original
    assert client.actions == ["module-browser-result"] * 24 + ["module-lesson"] * 24


@pytest.mark.parametrize("target", ["output", "notes", "source", "elapsed"])
def test_replacement_rejects_changed_output_drafts_notes_or_record_metadata(target: str) -> None:
    client = PersistenceClient()
    if target == "output":
        client.records["js-043"]["output"] += " changed after execution"
    elif target == "elapsed":
        client.records["js-043"]["elapsed_seconds"] = 99
    else:
        field = "explanation" if target == "notes" else "source"
        client.sessions["js-043"][field] += " changed"
    with pytest.raises(ValueError, match="changed after container replacement"):
        probe.verify_persistence(client, client.report)


def test_incomplete_execution_cannot_be_promoted_to_persistence_acceptance() -> None:
    client = PersistenceClient()
    client.report["passed"] = False
    with pytest.raises(ValueError, match="complete successful"):
        probe.verify_persistence(client, client.report)
    assert client.actions == []
