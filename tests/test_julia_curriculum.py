"""Independent source, scientific and optional runtime checks for Julia teaching."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses/julia"


@cache
def runtime_checks() -> dict[str, Any]:
    return runpy.run_path(str(COURSE / "authoring/check_runtime.py"))


def test_julia_route_and_runtime_contract() -> None:
    track = json.loads((COURSE / "track.json").read_text())
    manifest = json.loads((COURSE / "lessons.json").read_text())
    expected = [f"julia-{number:03}" for number in range(1, 33)]
    assert track["id"] == manifest["track_id"] == "julia"
    assert [row["id"] for row in track["lessons"]] == expected
    assert [row["id"] for row in manifest["lessons"]] == expected
    assert {row["level"] for row in track["lessons"]} == {"beginner", "intermediate", "advanced"}
    seen: set[str] = set()
    for row, implementation in zip(track["lessons"], manifest["lessons"], strict=True):
        assert set(row["prerequisites"]) <= seen
        seen.add(row["id"])
        assert implementation["language"] == implementation["runtime_profile"] == "julia"
        assert implementation["verification_id"] is None
        paths = [
            implementation["guide_path"],
            implementation["source_path"],
            *implementation["solution_paths"],
        ]
        assert len(set(paths)) == 4
        assert all((ROOT / path).is_file() for path in paths)


@pytest.mark.parametrize("number", range(1, 33))
def test_julia_unit_complete_sources_and_explanations(number: int) -> None:
    key = f"julia-{number:03}"
    row = json.loads((COURSE / "authoring" / f"unit-{number:03}.json").read_text())
    body = (COURSE / "authoring/chapters" / f"{key}.md").read_text()
    guide = (COURSE / "guides" / f"{key}.md").read_text()
    assert len(re.findall(r"\b\w+\b", body)) >= 450
    assert len(row["exercises"]) == len({entry["title"] for entry in row["exercises"]}) == 6
    assert len(row["sources"]) >= 2
    assert guide.count("```julia\n") == 2
    assert "{{WORKED_" not in guide
    assert "\u2014" not in guide
    assert "## Primary references" in guide and "## Six investigations" in guide
    for document, path in [(body, COURSE / "authoring/chapters"), (guide, COURSE / "guides")]:
        for link in re.findall(r"\]\(([^)]+)\)", document):
            if link.startswith("../"):
                assert (path / link).resolve().is_file(), link
    source = COURSE / "authoring/programs"
    for kind in ("learner", "reference", "worked_a", "worked_b"):
        text = (source / f"{key}_{kind}.jl").read_text()
        assert len(text.encode()) < 48_000
        assert "Pkg.add" not in text and "Downloads.download" not in text
        if kind.startswith("worked"):
            assert f"```julia\n{text}```" in guide
    assert (source / f"{key}_learner.jl").read_bytes() == (
        COURSE / "lessons" / f"{key}.jl"
    ).read_bytes()
    assert (source / f"{key}_reference.jl").read_bytes() == (
        COURSE / "solutions" / f"{key}_reference.jl"
    ).read_bytes()


def test_julia_generator_round_trip() -> None:
    result = subprocess.run(
        [sys.executable, str(COURSE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_julia_source_hashes_and_figure_requirements() -> None:
    contracts = json.loads((COURSE / "fixtures/reference-contracts.json").read_text())
    assert len(contracts["references"]) == 32
    for row in contracts["references"]:
        source = (ROOT / row["reference"]).read_bytes()
        assert row["profile"] == "julia"
        assert row["source_sha256"] == hashlib.sha256(source).hexdigest()
        assert row["expected_output"] in source.decode()
    figures = json.loads((COURSE / "figure-contracts.json").read_text())["units"]
    assert {row["id"] for row in figures} == {"julia-020", "julia-024", "julia-032"}
    assert all(
        row["count"] == 1
        and row["kind"] == "plotly"
        and row["description_required"]
        and row["table_required"]
        for row in figures
    )
    expected = runtime_checks()["expected_figures"]
    assert expected(20, "worked_a") == 0
    assert expected(20, "worked_b") == 1
    assert expected(24, "learner") == 1
    assert expected(32, "reference") == 1
    assert expected(32, "learner") == 0


def test_julia_capture_checker_rejects_missing_and_incomplete_charts() -> None:
    validate = runtime_checks()["validate_figures"]
    validate([], 0)
    with pytest.raises(ValueError, match="Expected 1"):
        validate([], 1)
    with pytest.raises(ValueError, match="description"):
        validate([{"kind": "plotly"}], 1)
    chart: dict[str, Any] = {
        "kind": "plotly",
        "description": "Two points",
        "figure": {
            "data": [{"x": [1, 2], "y": [3, 4]}],
            "layout": {
                "meta": {
                    "description": "Exact values",
                    "table": {"columns": ["x", "y"], "rows": [[1, 3], [2, 4]]},
                }
            },
        },
    }
    validate([chart], 1)
    chart["figure"]["layout"]["meta"]["table"]["rows"] = [[1]]
    with pytest.raises(ValueError, match="columns"):
        validate([chart], 1)


def residual(row: dict[str, str], intercept: Fraction, slope: Fraction) -> Fraction:
    return intercept + slope * Fraction(row["x"]) - Fraction(row["y"])


def squared_residual(row: dict[str, str], intercept: Fraction, slope: Fraction) -> Fraction:
    value = residual(row, intercept, slope)
    return value * value


def test_julia_capstone_fixture_and_independent_rational_oracle() -> None:
    text = (COURSE / "fixtures/sensor-calibration.csv").read_text()
    rows = list(csv.DictReader(io.StringIO(text)))
    assert len(rows) == len({row["id"] for row in rows}) == 8
    assert all(row["feature_available_at"] <= row["prediction_at"] for row in rows)
    assert all(row["label_available_at"] <= "2024-01-10" for row in rows)
    programs = COURSE / "authoring/programs"
    for kind in ("learner", "reference", "worked_a", "worked_b"):
        source = (programs / f"julia-032_{kind}.jl").read_text()
        embedded = re.search(r'const SENSOR_CSV = """(.*?)"""', source, re.DOTALL)
        assert embedded and embedded[1] == text
    train = [row for row in rows if row["split"] == "train"]
    x, y = [Fraction(row["x"]) for row in train], [Fraction(row["y"]) for row in train]
    count, sum_x, sum_y = Fraction(len(x)), sum(x), sum(y)
    sum_xx = sum(value * value for value in x)
    sum_xy = sum(a * b for a, b in zip(x, y, strict=True))
    errors: dict[int, Fraction] = {}
    coefficients: dict[int, tuple[Fraction, Fraction]] = {}
    for penalty in (0, 1, 2, 4):
        determinant = count * (sum_xx + penalty) - sum_x * sum_x
        intercept = ((sum_xx + penalty) * sum_y - sum_x * sum_xy) / determinant
        slope = (count * sum_xy - sum_x * sum_y) / determinant
        coefficients[penalty] = (intercept, slope)
        development = [row for row in rows if row["split"] == "development"]
        errors[penalty] = sum(
            (squared_residual(row, intercept, slope) for row in development), Fraction(0)
        ) / len(development)
    chosen = min(errors, key=lambda penalty: errors[penalty])
    assert chosen == 2
    assert coefficients[chosen] == (Fraction(12, 7), Fraction(13, 7))
    assert errors[chosen] == Fraction(1, 98)
    intercept, slope = coefficients[chosen]
    final = [row for row in rows if row["split"] == "final"]
    final_error = sum(
        (squared_residual(row, intercept, slope) for row in final), Fraction(0)
    ) / len(final)
    assert final_error == Fraction(5, 98)


def test_julia_independent_contracts_in_prepared_host_runtime() -> None:
    executable = shutil.which("julia")
    project = Path(os.environ.get("DS60_JULIA_PROJECT", "/opt/julia-env"))
    if executable is None or not (project / "Project.toml").is_file():
        pytest.skip(
            "Julia and the prepared package environment require separate worker qualification"
        )
    result = subprocess.run(
        [
            sys.executable,
            str(COURSE / "authoring/check_runtime.py"),
            "--julia",
            executable,
            "--project",
            str(project),
            "--independent-only",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
