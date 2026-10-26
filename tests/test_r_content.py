"R authoring, source-parity and learning-contract checks; no implicit execution."

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses/r"
spec = importlib.util.spec_from_file_location("r_course_authoring", COURSE / "authoring/build.py")
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
UNITS = builder.units()


def test_full_route_preserves_ids_and_direct_prerequisite_graph() -> None:
    assert [u["id"] for u in UNITS] == [f"r-{n:03}" for n in range(1, 61)]
    known: set[str] = set()
    for unit in UNITS:
        assert set(unit["prerequisites"]) <= known
        assert len(unit["prerequisites"]) == len(set(unit["prerequisites"]))
        known.add(unit["id"])
    assert UNITS[0]["prerequisites"] == []
    assert UNITS[40]["prerequisites"] == ["r-040"]
    assert {u["level"] for u in UNITS} == {"beginner", "intermediate", "advanced"}
    admission = json.loads((COURSE / "lessons.json").read_text())
    assert len(admission["lessons"]) == 60
    for unit in admission["lessons"]:
        assert unit["language"] == "r" and unit["runtime_profile"] == "r-statistics"
        assert unit["verification_id"] is None
        assert unit["source_path"].endswith(".R")


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u["id"])
def test_independent_programs_and_explained_behavioral_contracts(unit: dict[str, Any]) -> None:
    assert len(unit["worked_examples"]) >= 2
    assert len(unit["exercises"]) == 6
    assert len({e["prompt"] for e in unit["exercises"]}) == 6
    assert all(e["hint"] and e["answer"] and e["expected"] for e in unit["exercises"])
    assert len(unit["vocabulary"]) >= 4
    assert unit["mechanism"].count("\n\n") >= 3
    assert all(e["explanation"] and e["expected"] for e in unit["worked_examples"])
    assert all("stopifnot(" in e["code"] for e in unit["worked_examples"])
    assert "stopifnot(" in unit["reference"]
    assert f"{unit['id']} reference checks passed" in unit["reference"]
    assert unit["starter"] != unit["reference"]
    assert "TODO" in unit["starter"]
    assert not re.search(r"stop\s*\(\s*['\"]TODO", unit["starter"])
    code = "\n".join(
        [unit["starter"], unit["reference"], *[e["code"] for e in unit["worked_examples"]]]
    )
    for forbidden in ["install.packages(", "download.file(", "http://", "https://"]:
        assert forbidden not in code
    assert all(s["url"].startswith("https://") and s["title"] for s in unit["sources"])


def test_generated_source_and_markdown_are_exactly_bound_to_units() -> None:
    for relative, expected in builder.artifacts().items():
        assert (ROOT / relative).read_text() == expected, relative
        assert "\u2014" not in expected
        assert not any(ord(c) < 32 and c not in "\n\t\r" for c in expected)
    for unit in UNITS:
        key = unit["id"]
        guide = (COURSE / f"guides/{key}.md").read_text()
        blocks = re.findall(r"```r\n(.*?)\n```", guide, re.S)
        assert blocks == [e["code"].rstrip() for e in unit["worked_examples"]]
        assert (COURSE / f"lessons/{key}.R").read_text() == unit["starter"].rstrip() + "\n"
        reference = (COURSE / f"solutions/{key}_reference.R").read_text()
        assert reference.endswith(unit["reference"].rstrip() + "\n")
        assert "fresh offline R process" in guide
        assert "at most two" in guide


def test_required_language_and_analysis_mechanisms_remain_explicit() -> None:
    by_id = {u["id"]: u for u in UNITS}
    assert "force(" in by_id["r-013"]["reference"]
    assert "drop = FALSE" in by_id["r-010"]["reference"]
    assert "on.exit(" in by_id["r-015"]["reference"]
    assert "anyDuplicated" in by_id["r-033"]["reference"]
    assert "reshape(" in by_id["r-034"]["reference"]
    assert "qr(" in by_id["r-039"]["reference"]
    assert "empty_result" in by_id["r-040"]["reference"]
    for number, name in [(21, "S3"), (22, "S4"), (23, "R6"), (24, "S7")]:
        unit = by_id[f"r-{number:03}"]
        assert name in unit["title"] + unit["mechanism"]
    assert "survival::coxph" in by_id["r-048"]["reference"]
    assert "rpart::rpart" in by_id["r-047"]["reference"]
    assert "ggplotly" in by_id["r-059"]["reference"]
    assert "error_y" in by_id["r-060"]["reference"]
