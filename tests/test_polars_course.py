"""Source and independent semantic contracts for the Polars learning path."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/polars"


def load_reference(number: int) -> ModuleType:
    pytest.importorskip("polars", reason="Prepared data-engineering runtime required")
    path = BASE / "references" / f"polars-{number:03}_reference.py"
    spec = importlib.util.spec_from_file_location(f"polars_reference_{number}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_polars_manifest_and_teaching_contract() -> None:
    plan = json.loads((BASE / "track.json").read_text())
    manifest = json.loads((BASE / "lessons.json").read_text())
    assert [row["id"] for row in plan["lessons"]] == [f"polars-{n:03}" for n in range(1, 19)]
    assert {row["level"] for row in plan["lessons"]} == {"beginner", "intermediate", "advanced"}
    assert len(manifest["lessons"]) == 18
    for unit in manifest["lessons"]:
        assert unit["runtime_profile"] == "data-engineering" and unit["language"] == "python"
        assert unit["verification_id"] is None
        paths = [unit["guide_path"], unit["source_path"], *unit["solution_paths"]]
        assert len(paths) == len(set(paths)) == 4
        assert all((ROOT / name).is_file() for name in paths)
        guide = (ROOT / unit["guide_path"]).read_text()
        assert guide.count("## Worked case ") == 2
        assert all(f"### {n}. " in guide for n in range(1, 7))
        prose = re.sub(r"```.*?```", "", guide, flags=re.S)
        assert len(prose.split()) >= 600
        assert "—" not in guide
        assert "## Diagnose errors and misleading results" in guide


def test_polars_authoring_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(BASE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("number", range(1, 19))
def test_polars_complete_reference_cases(number: int) -> None:
    module = load_reference(number)
    first, second = module.example_one(), module.example_two()
    assert isinstance(first, dict) and first
    assert isinstance(second, dict) and second


def test_polars_join_and_availability_oracles() -> None:
    joined = load_reference(6).example_one()
    assert joined["correct_total"] == sum([5, 7, 9])
    assert joined["fanout_total"] == sum([5, 5, 7, 7, 9])
    temporal = load_reference(14).example_two()
    records = [(2, 3, 10), (4, 7, 999), (8, 8, 30)]
    expected = [
        max((r for r in records if r[0] <= cutoff and r[1] <= cutoff), key=lambda r: (r[0], r[1]))[
            2
        ]
        for cutoff in (5, 9)
    ]
    assert temporal["available_values"] == expected == [10, 30]
    assert temporal["event_time_only_values"] != expected


def test_polars_column_context_and_weighting_are_distinct() -> None:
    contexts = load_reference(2).example_one()
    assert [row["old_x_times_ten"] for row in contexts["parallel_context"]] == [10, 20, 30]
    assert [row["new_x_times_ten"] for row in contexts["explicit_dependency"]] == [20, 30, 40]
    rates: dict[str, Any] = load_reference(5).example_one()
    assert rates["weighted_rates"][0]["rate"] == (1 + 9) / (1 + 99)
    assert rates["wrong_equal_row_mean"] != rates["weighted_rates"][0]["rate"]
