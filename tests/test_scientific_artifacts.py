"""Scientific gates reject lost figures and preserve source-bound evidence."""

from __future__ import annotations

import base64
import copy
import struct
import zlib
from pathlib import Path
from typing import Any

import pytest

from scripts import check_scientific_artifacts as gate
from scripts.check_module_references import ReferenceCase, verify_result

ROOT = Path(__file__).resolve().parents[1]


def plot() -> dict[str, Any]:
    return {
        "kind": "plotly",
        "figure": {
            "data": [{"type": "scatter", "x": [1], "y": [2]}],
            "layout": {
                "meta": {
                    "description": "One measured point.",
                    "table": {"columns": ["x", "y"], "rows": [[1, 2]]},
                }
            },
        },
    }


def png() -> dict[str, str]:
    def chunk(kind: bytes, content: bytes) -> bytes:
        return (
            struct.pack(">I", len(content))
            + kind
            + content
            + struct.pack(">I", zlib.crc32(kind + content) & 0xFFFFFFFF)
        )

    raw = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw += chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b"")
    return {"kind": "png", "data": base64.b64encode(raw).decode()}


@pytest.fixture
def case(monkeypatch: pytest.MonkeyPatch) -> ReferenceCase:
    item = ReferenceCase(
        "viz-test",
        "data-visualization",
        "python-core",
        "python",
        "practice",
        None,
        "courses/example.py",
        "print(1)\n",
    )
    monkeypatch.setattr(
        gate,
        "CONTRACTS",
        {
            item.lesson_id: {
                "profile": item.profile,
                "source_path": item.source_path,
                "source_sha256": item.source_sha256,
                "kinds": ["plotly"],
                "table_rows": 1,
            }
        },
    )
    monkeypatch.setattr(gate, "references", lambda profiles, root=ROOT: [item])
    return item


def test_reviewed_inventory_binds_all_eight_python_and_ten_actual_r_references() -> None:
    assert [c.lesson_id for c in gate.references(["python-core"])] == [
        f"viz-{n:03}" for n in range(1, 9)
    ]
    assert [c.lesson_id for c in gate.references(["r-statistics"])] == [
        f"r-{n:03}" for n in range(51, 61)
    ]
    assert "r-025" not in gate.CONTRACTS  # ggplot_build alone does not print a figure.
    assert gate.CONTRACTS["r-059"]["kinds"] == ["png", "plotly"]


def test_missing_capture_fails_even_when_computation_succeeded(case: ReferenceCase) -> None:
    job = {
        "job_id": "job",
        "lesson_id": case.lesson_id,
        "profile": case.profile,
        "source_sha256": case.source_sha256,
        "status": "succeeded",
        "returncode": 0,
        "truncated": False,
        "checks": [],
        "artifacts": [],
    }
    with pytest.raises(ValueError, match="expected figures"):
        verify_result(case, "job", job)
    job["artifacts"] = [plot()]
    verify_result(case, "job", job)


def test_source_change_requires_explicit_contract_review(case: ReferenceCase) -> None:
    with pytest.raises(ValueError, match="stale"):
        gate.verify_figures(case.lesson_id, case.source + "# changed\n", [plot()])


def test_accessible_table_and_description_are_required(case: ReferenceCase) -> None:
    for missing in ("description", "table"):
        figure = plot()
        del figure["figure"]["layout"]["meta"][missing]
        with pytest.raises(ValueError, match="description/table"):
            gate.verify_figures(case.lesson_id, case.source, [figure])


def test_png_gate_rejects_header_only_and_corrupt_image_payloads(
    case: ReferenceCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate.CONTRACTS[case.lesson_id]["kinds"] = ["png"]
    good = png()
    result = gate.verify_figures(case.lesson_id, case.source, [good])
    assert result is not None
    assert result["count"] == 1
    raw = base64.b64decode(good["data"])
    for damaged in (raw[:24], raw[:-1], raw[:45] + bytes([raw[45] ^ 1]) + raw[46:]):
        with pytest.raises(ValueError):
            gate.verify_figures(
                case.lesson_id,
                case.source,
                [{"kind": "png", "data": base64.b64encode(damaged).decode()}],
            )


class Client:
    def __init__(self, case: ReferenceCase, *, capture: bool = True) -> None:
        self.case = case
        self.session = {"source": "# prior draft\n", "prediction": "retain this note"}
        self.original = copy.deepcopy(self.session)
        self.capture = capture
        self.jobs: dict[str, dict[str, Any]] = {}
        self.actions: list[str] = []

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append(action)
        if action == "module-readiness":
            return {"profiles": [{"profile": self.case.profile, "ready": True}]}
        if action == "module-lesson":
            return {
                "id": self.case.lesson_id,
                "runtime_profile": self.case.profile,
                "language": self.case.language,
                "learning_mode": self.case.learning_mode,
                "verification_id": None,
                "source": self.case.source,
                "session": copy.deepcopy(self.session),
                "history": [{"job_id": key} for key in self.jobs],
            }
        if action == "module-save":
            self.session.update(fields["fields"])
            return {}
        if action == "module-run":
            key = fields["request_id"]
            self.jobs[key] = {
                "job_id": key,
                "lesson_id": self.case.lesson_id,
                "profile": self.case.profile,
                "source_sha256": self.case.source_sha256,
                "status": "succeeded",
                "returncode": 0,
                "truncated": False,
                "checks": [],
                "output": "done\n",
                "artifacts": [plot()] if self.capture else [],
            }
            return self.jobs[key]
        if action == "module-job":
            return copy.deepcopy(self.jobs[fields["job_id"]])
        raise AssertionError(action)


def test_actual_receipts_restore_prior_drafts_and_persistence_only_reads(
    case: ReferenceCase,
) -> None:
    client = Client(case)
    report = gate.qualify(client, ["python-core"])
    assert report["passed"] and gate.pad_digest(client.session) == gate.pad_digest(client.original)
    client.actions.clear()
    result = gate.verify_persistence(client, report, ["python-core"])
    assert result["passed"]
    assert set(client.actions) == {"module-job", "module-lesson"}
    assert report["receipts"][0]["count"] == 1


def test_failed_figure_capture_still_restores_the_original_source(case: ReferenceCase) -> None:
    client = Client(case, capture=False)
    with pytest.raises(ValueError, match="expected figures"):
        gate.qualify(client, ["python-core"])
    assert gate.pad_digest(client.session) == gate.pad_digest(client.original)
    assert client.actions.count("module-run") == 1


def test_readback_rejects_changed_figure_or_draft_without_replay(case: ReferenceCase) -> None:
    client = Client(case)
    report = gate.qualify(client, ["python-core"])
    key = report["receipts"][0]["job_id"]
    client.jobs[key]["artifacts"][0]["figure"]["data"][0]["y"] = [9]
    client.actions.clear()
    with pytest.raises(ValueError, match="changed"):
        gate.verify_persistence(client, report, ["python-core"])
    assert not {"module-run", "module-save", "module-cancel"} & set(client.actions)
    client.jobs[key]["artifacts"] = [plot()]
    client.session["source"] = "different draft"
    with pytest.raises(ValueError, match="source/history"):
        gate.verify_persistence(client, report, ["python-core"])
