"""Paired scientific figure semantics, content admission and bounded outputs."""

from __future__ import annotations

import ast
import json
import re
import runpy
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ds60sqlpy.modules import ModuleCatalog
from ds60sqlpy.plot_artifacts import validate_artifacts

go = pytest.importorskip("plotly.graph_objects")

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "courses" / "data-visualization"
INVENTORY = json.loads((SUBJECT / "fixtures" / "plotly-inventory.json").read_text())


@pytest.fixture(scope="module")
def python_figures() -> list[Any]:
    namespace = runpy.run_path(str(SUBJECT / "authoring" / "python_cases.py"))
    return [namespace[f"case_{number:02d}"]() for number in range(1, 9)]


def test_paired_subject_admits_all_three_stages_and_preserves_variant_identity() -> None:
    catalog = ModuleCatalog(ROOT)
    plan = json.loads((SUBJECT / "track.json").read_text())
    assert {row["level"] for row in plan["lessons"]} == {"beginner", "intermediate", "advanced"}
    for row in INVENTORY:
        canonical = catalog.get(row["id"])
        browser = catalog.get(row["id"] + "@javascript")
        assert canonical.runtime_profile == "python-core" and canonical.language == "python"
        assert browser.runtime_profile == "javascript-browser" and browser.language == "javascript"
        assert canonical.source_path != browser.source_path
        guide = ROOT / canonical.guide_path
        text = guide.read_text()
        assert "## Six progressive exercises" in text
        assert "## Ask an AI tutor about this lesson" in text and "\u2014" not in text
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if target.startswith(("http:", "https:", "#")):
                continue
            assert (guide.parent / target.split("#", 1)[0]).resolve().exists(), target


def test_numeric_encodings_preserve_density_pairing_and_extrema(python_figures: list[Any]) -> None:
    density = python_figures[1]
    rows = density.layout.meta["table"]["rows"]
    assert [row[2] for row in rows] == [4, 2, 2, 2]
    assert sum((row[1] - row[0]) * row[3] for row in rows) == pytest.approx(1)
    assert list(density.data[1].x)[:3] == [0, 1, 2]
    assert list(density.data[1].y)[:3] == [0, 0.2, 0.4]
    paired = python_figures[5].layout.meta["table"]["rows"]
    independently_computed = [(row[2] - row[1]) ** 2 - (row[3] - row[1]) ** 2 for row in paired]
    assert np.mean(independently_computed) == pytest.approx(-0.3775)
    reduced = python_figures[6]
    assert 2473 in reduced.data[1].x and 2473 not in reduced.data[0].x
    assert max(reduced.data[1].y) == 12 and len(reduced.data[1].x) <= 102


def test_error_bars_store_distances_rather_than_endpoints(python_figures: list[Any]) -> None:
    trace = python_figures[2].data[0]
    lower = np.asarray(trace.x) - np.asarray(trace.error_x.arrayminus)
    upper = np.asarray(trace.x) + np.asarray(trace.error_x.array)
    assert np.allclose(lower, [-0.596, -0.388, 0.408])
    assert np.allclose(upper, [-0.204, 0.788, 1.192])


def test_python_and_javascript_have_matching_scientific_tables(python_figures: list[Any]) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("JavaScript semantic comparison requires the prepared Node toolchain")
    source = SUBJECT / "authoring" / "browser_cases.js"
    script = "const fs=require('fs');const vm=require('vm');const c=vm.createContext({console});"
    script += "vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),c);"
    script += (
        "process.stdout.write(vm.runInContext('JSON.stringify(Array.from({"
        "length:8},(_,i)=>specifications[i+1]().rows))',c));"
    )
    result = subprocess.run(
        [node, "-e", script, str(source)], capture_output=True, text=True, check=True
    )
    browser_tables = json.loads(result.stdout)
    for python_figure, browser_rows in zip(python_figures, browser_tables, strict=True):
        python_rows = python_figure.layout.meta["table"]["rows"]
        assert len(python_rows) == len(browser_rows)
        for left, right in zip(python_rows, browser_rows, strict=True):
            assert len(left) == len(right)
            for a, b in zip(left, right, strict=True):
                if isinstance(a, (int, float)) and not isinstance(a, bool):
                    assert a == pytest.approx(b)
                else:
                    assert a == b


def test_browser_starters_expose_their_fixture_without_claiming_completion() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Browser scaffold checks require the prepared Node toolchain")
    script = """
const fs = require('fs');
const vm = require('vm');
const rows = process.argv.slice(1).map(path => {
  const tables = [], logs = [];
  const context = vm.createContext({console: {
    table(value) { tables.push(value); },
    log(value) { logs.push(value); }
  }});
  vm.runInContext(fs.readFileSync(path, 'utf8'), context);
  return {tables, logs};
});
process.stdout.write(JSON.stringify(rows));
"""
    paths = [str(SUBJECT / "lessons" / f"viz-{number:03}.js") for number in range(1, 9)]
    result = subprocess.run(
        [node, "-e", script, *paths], capture_output=True, text=True, check=True
    )
    rows = json.loads(result.stdout)
    assert len(rows) == 8 and all(len(row["tables"]) == 1 for row in rows)
    assert rows[0]["tables"][0][2] == ["u3", "Gamma", 3]
    assert rows[1]["tables"][0][-1] is None
    assert rows[6]["tables"][0]["spike_index"] == 2473
    assert rows[7]["tables"][0] == {"completed": 8, "pending": 3, "failed": 1}
    assert not any("Plotly complete" in message for row in rows for message in row["logs"])


@pytest.mark.parametrize("row", INVENTORY, ids=lambda row: row["id"])
def test_complete_python_reference_captures_one_bounded_accessible_figure(
    row: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured: list[Any] = []
    monkeypatch.setattr(go.Figure, "show", lambda figure, *args, **kwargs: captured.append(figure))
    runpy.run_path(str(ROOT / row["python_reference"]), run_name="__main__")
    assert len(captured) == 1
    figure = captured[0]
    payload = json.loads(figure.to_json())
    checked = validate_artifacts([{"kind": "plotly", "figure": payload}])
    assert checked[0]["table"] == payload["layout"]["meta"]["table"]
    assert len(figure.to_json().encode()) <= 200 * 1024
    metadata = payload["layout"]["meta"]
    assert len(metadata["description"]) <= 2000
    assert len(metadata["table"]["rows"]) == row["expected_table_rows"]
    assert all(isinstance(column, str) for column in metadata["table"]["columns"])
    assert row["marker"] in capsys.readouterr().out
    for trace in payload["data"]:
        assert trace["type"] in {"bar", "scatter"}
    tree = ast.parse((ROOT / row["python_reference"]).read_text())
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not imported & {"requests", "socket", "urllib"}
