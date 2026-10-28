"""Semantic boundaries for structured, immutable scientific output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.module_extensions import load_extra_plans
from ds60sqlpy.plot_artifacts import (
    publish_report,
    publish_table,
    read_artifacts,
    validate_artifacts,
)


def test_reports_retain_scalar_types_and_literal_markup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    publish_table(
        ["name", "value"],
        [["<script>literal</script>", None], ["zero", 0], ["flag", False]],
        description="Exact table",
    )
    publish_report({"metadata": {"count": 2, "literal": "<img src=x>"}}, description="Model report")
    artifacts, warning = read_artifacts(tmp_path)
    assert not warning
    assert artifacts[0]["table"]["rows"] == [
        ["<script>literal</script>", None],
        ["zero", 0],
        ["flag", False],
    ]
    assert artifacts[1]["data"]["metadata"] == {"count": 2, "literal": "<img src=x>"}
    assert not list(tmp_path.glob(".ds60-output-*"))


@pytest.mark.parametrize("data", [float("nan"), float("inf"), {1: "key"}, {"deep": object()}])
def test_invalid_report_does_not_overwrite_prior_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: Any
) -> None:
    monkeypatch.chdir(tmp_path)
    publish_report({"accepted": 7}, description="Original")
    before = (tmp_path / "ds60-figures.json").read_bytes()
    with pytest.raises((TypeError, ValueError)):
        publish_report(data, description="Invalid")
    assert (tmp_path / "ds60-figures.json").read_bytes() == before


def test_output_limit_preserves_first_two(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    publish_report({"a": 1}, description="A")
    publish_table(["b"], [[2]], description="B")
    before = (tmp_path / "ds60-figures.json").read_bytes()
    with pytest.raises(ValueError):
        publish_report({"c": 3}, description="C")
    assert (tmp_path / "ds60-figures.json").read_bytes() == before


def test_publisher_does_not_follow_output_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    outside = tmp_path / "retained.json"
    outside.write_text("[]")
    (tmp_path / "ds60-figures.json").symlink_to(outside)
    with pytest.raises(ValueError):
        publish_report({"x": 1}, description="Blocked")
    assert outside.read_text() == "[]"


@pytest.mark.parametrize(
    "table",
    [
        {"columns": ["a"], "rows": [[1, 2]]},
        {"columns": ["a"], "rows": [[1]] * 101},
        {"columns": ["a"], "rows": [[float("nan")]]},
    ],
)
def test_table_shape_and_bounds_are_enforced(table: Any) -> None:
    with pytest.raises(ValueError):
        validate_artifacts([{"kind": "table", "description": "Bounded", "table": table}])


def test_explicit_tutorial_mode_and_legacy_default(tmp_path: Path) -> None:
    folder = tmp_path / "courses" / "example"
    folder.mkdir(parents=True)
    plan = {
        "schema_version": 1,
        "id": "example",
        "title": "Examples",
        "summary": "Worked cases",
        "lessons": [
            {
                "id": f"example-{i:03}",
                "title": "Case",
                "level": level,
                "minutes": 30,
                "prerequisites": [],
                "runtime": "python-core",
                "concepts": ["example"],
                "outcome": "Explain a result",
                "lab": "Inspect the example",
                "verification": "Compare the stated result",
            }
            for i, level in enumerate(("beginner", "intermediate", "advanced"), 1)
        ],
    }
    path = folder / "track.json"
    path.write_text(json.dumps(plan))
    assert load_extra_plans(tmp_path, {"python-core"})[0][0]["learning_mode"] == "practice"
    plan["learning_mode"] = "tutorial"
    path.write_text(json.dumps(plan))
    assert load_extra_plans(tmp_path, {"python-core"})[0][0]["learning_mode"] == "tutorial"
    invalid_values: tuple[object, ...] = (True, [], "execute-anything")
    for invalid in invalid_values:
        plan["learning_mode"] = invalid
        path.write_text(json.dumps(plan))
        with pytest.raises(ValueError, match="learning mode"):
            load_extra_plans(tmp_path, {"python-core"})


def test_large_integer_requires_explicit_text_representation() -> None:
    with pytest.raises(ValueError, match="identifiers as strings"):
        validate_artifacts([{"kind": "json", "description": "Identifier", "data": {"id": 2**60}}])
    assert validate_artifacts(
        [{"kind": "json", "description": "Identifier", "data": {"id": str(2**60)}}]
    )[0]["data"]["id"] == str(2**60)
