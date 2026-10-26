"""Offline references cannot become execution receipts or escape the course."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.module_drafts import draft_capability, worked_examples


def fixture(root: Path) -> tuple[Path, dict[str, Any]]:
    folder = root / "courses/dax"
    folder.mkdir(parents=True)
    source = b'EVALUATE ROW("Revenue", 187)\n'
    data = b"Revenue\n187\n"
    (folder / "reference.dax").write_bytes(source)
    (folder / "sales.csv").write_bytes(data)
    model = {
        "schema_version": 1,
        "tables": [
            {
                "name": "Sales",
                "path": "courses/dax/sales.csv",
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        ],
    }
    model_bytes = json.dumps(model).encode()
    (folder / "model.json").write_bytes(model_bytes)
    item = {
        "lesson_id": "dax-001",
        "reference_path": "courses/dax/reference.dax",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "model_path": "courses/dax/model.json",
        "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "evidence": "hand-derived",
        "cases": [
            {
                "id": "a",
                "title": "All rows",
                "context": "No filters",
                "trace": ["Sum revenue"],
                "columns": [{"name": "Revenue", "type": "number"}],
                "rows": [[187], [None]],
                "note": "Not calculated from the current draft.",
            }
        ],
    }
    payload = {"schema_version": 1, "track_id": "dax", "lessons": [item]}
    path = folder / "reference-results.json"
    path.write_text(json.dumps(payload))
    return path, payload


def test_reference_is_source_bound_and_never_execution(tmp_path: Path) -> None:
    fixture(tmp_path)
    cap = draft_capability("dax-offline")
    assert cap["ready"] and cap["can_run"] is False and cap["mode"] == "draft"
    result = worked_examples(tmp_path, "dax-001")
    assert result["executed"] is False and result["evidence"] == "hand-derived"
    assert result["cases"][0]["rows"] == [[187], [None]]
    (tmp_path / "courses/dax/sales.csv").write_text("Revenue\n188\n")
    with pytest.raises(ValueError, match="stale"):
        worked_examples(tmp_path, "dax-001")


@pytest.mark.parametrize(
    "change",
    ["escape", "symlink", "digest", "runtime", "duplicate", "number", "row", "too_many", "missing"],
)
def test_refuse_unsafe_or_misleading_worked_reference(tmp_path: Path, change: str) -> None:
    path, payload = fixture(tmp_path)
    entry = payload["lessons"][0]
    if change == "escape":
        entry["reference_path"] = "courses/dax/../../private.dax"
    elif change == "symlink":
        reference = tmp_path / entry["reference_path"]
        reference.rename(reference.with_name("actual.dax"))
        reference.symlink_to("actual.dax")
    elif change == "digest":
        entry["source_sha256"] = "0" * 64
    elif change == "runtime":
        entry["evidence"] = "executed"
    elif change == "duplicate":
        payload["lessons"].append(entry.copy())
    elif change == "number":
        entry["cases"][0]["rows"] = [[float("nan")]]
    elif change == "row":
        entry["cases"][0]["rows"] = [[1, 2]]
    elif change == "too_many":
        entry["cases"][0]["rows"] = [[1]] * 101
    else:
        entry["lesson_id"] = "dax-002"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        worked_examples(tmp_path, "dax-001")
