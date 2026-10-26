"""Contracts for the advanced R statistics and visualization source units."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "courses/r/authoring/units"
UNITS = [
    json.loads((DIRECTORY / f"r-{number:03d}.json").read_text(encoding="utf-8"))
    for number in range(41, 61)
]
FIELDS = {
    "id",
    "title",
    "level",
    "minutes",
    "prerequisites",
    "concepts",
    "outcome",
    "mechanism",
    "vocabulary",
    "anatomy",
    "worked_examples",
    "exercises",
    "starter",
    "reference",
    "solution_explanation",
    "sources",
}


def test_advanced_slice_has_exact_ownership_and_a_coherent_handoff() -> None:
    assert [unit["id"] for unit in UNITS] == [f"r-{number:03d}" for number in range(41, 61)]
    assert UNITS[0]["prerequisites"] == ["r-040"]
    for unit in UNITS:
        assert set(unit) == FIELDS
        number = int(unit["id"].split("-")[1])
        assert all(int(parent.split("-")[1]) < number for parent in unit["prerequisites"])
        assert unit["level"] in {"intermediate", "advanced"}
        assert 90 <= unit["minutes"] <= 180


@pytest.mark.parametrize("unit", UNITS, ids=lambda unit: unit["id"])
def test_source_units_explain_mechanisms_and_distinct_cases(unit: dict[str, Any]) -> None:
    assert len(unit["mechanism"].split()) >= 220
    assert len(unit["mechanism"].split("\n\n")) >= 4
    assert len(unit["vocabulary"]) >= 4
    assert all(set(item) == {"term", "definition"} for item in unit["vocabulary"])
    assert len(unit["worked_examples"]) >= 2
    assert len(unit["exercises"]) == 6
    assert len({item["prompt"] for item in unit["exercises"]}) == 6
    for example in unit["worked_examples"]:
        assert set(example) == {"title", "code", "explanation", "expected"}
        assert "stopifnot(" in example["code"]
        assert example["explanation"] and example["expected"]
    for exercise in unit["exercises"]:
        assert set(exercise) == {"prompt", "hint", "answer", "expected"}
        assert all(exercise.values())
    assert unit["reference"].count("stopifnot(") >= 4
    assert f"{unit['id']} reference checks passed" in unit["reference"]
    assert unit["starter"] != unit["reference"]
    assert len(re.findall(r"^# Exercise [1-6]:", unit["starter"], re.M)) == 6
    assert "results <- vector" in unit["starter"]
    assert 'stop("TODO' not in unit["starter"]


@pytest.mark.parametrize("unit", UNITS, ids=lambda unit: unit["id"])
def test_code_remains_offline_and_prose_is_readable(unit: dict[str, Any]) -> None:
    code = "\n".join(
        [unit["starter"], unit["reference"], *[case["code"] for case in unit["worked_examples"]]]
    )
    for forbidden in ("install.packages(", "download.file(", "http://", "https://", "system("):
        assert forbidden not in code
    text = json.dumps(unit, ensure_ascii=False)
    assert "\u2014" not in text
    for slogan in ("place to learn and grow", "one at a time", "unlock your"):
        assert slogan not in text.lower()
    prose = " ".join(
        [unit["mechanism"], unit["anatomy"], unit["solution_explanation"]]
        + [item[field] for item in unit["exercises"] for field in ("prompt", "answer", "expected")]
    )
    compact = set(re.findall(r"\b[A-Za-z]{2,}\d+(?:[./]\d+)?", prose))
    assert compact <= {"ggplot2", "log10"}
    assert unit["sources"]
    assert all(set(source) == {"title", "url"} for source in unit["sources"])
    assert all(source["url"].startswith("https://") for source in unit["sources"])


def test_graphics_units_retain_explicit_output_and_evidence_boundaries() -> None:
    by_id = {unit["id"]: unit for unit in UNITS}
    for number in range(53, 61):
        unit = by_id[f"r-{number:03d}"]
        assert "print(" in unit["reference"]
        explanation = (unit["mechanism"] + unit["solution_explanation"]).lower()
        assert any(boundary in explanation for boundary in ("browser", "visual"))
    assert "survival::coxph" in by_id["r-048"]["reference"]
    assert "rpart::rpart" in by_id["r-047"]["reference"]
    assert "customdata" in by_id["r-058"]["reference"]
    assert "ggplotly" in by_id["r-059"]["reference"]
    assert "error_y" in by_id["r-060"]["reference"]
