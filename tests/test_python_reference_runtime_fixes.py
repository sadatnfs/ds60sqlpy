"""Regression proofs for two failures found by the full cold notebook audit."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def code_cells(day: int) -> list[str]:
    path = next((ROOT / "python/ds-60day/solutions").glob(f"day{day:02d}*/*solutions.ipynb"))
    notebook = json.loads(path.read_text())
    return ["".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code"]


def test_altair_bounded_parameter_builds_a_valid_constant_bin_layer_menu() -> None:
    alt = pytest.importorskip("altair")
    pd = pytest.importorskip("pandas")
    source = next(source for source in code_cells(26) if "def altair_histogram" in source)
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "altair_histogram"
    )
    namespace = {"alt": alt, "pd": pd}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "day26-builder", "exec"), namespace)
    frame = pd.DataFrame(
        {"total_bill": [10.0, 20.0, 25.0, 40.0], "time": ["Lunch", "Dinner", "Lunch", "Dinner"]}
    )
    chart = namespace["altair_histogram"](frame)
    spec = chart.to_dict(validate=True)
    parameter = spec["params"][0]
    assert parameter["name"] == "histogram_bins" and parameter["value"] == 40
    assert parameter["bind"] == {
        "input": "range",
        "min": 10,
        "max": 80,
        "step": 5,
        "name": "Maximum bins: ",
    }
    assert [layer["encoding"]["x"]["bin"]["maxbins"] for layer in spec["layer"]] == list(
        range(10, 85, 5)
    )
    assert [layer["transform"][0]["filter"] for layer in spec["layer"]] == [
        f"histogram_bins === {value}" for value in range(10, 85, 5)
    ]
    assert "select" not in parameter
    for options in [(), (1, 40), (10, 101), (10, 10), (True, 40), (10, 40, 80)]:
        with pytest.raises(ValueError):
            namespace["altair_histogram"](frame, options=options)


def test_private_package_reference_imports_real_files_and_cleans_its_project(
    tmp_path: Path,
) -> None:
    source = next(source for source in code_cells(58) if "PYTEST_DISABLE_PLUGIN_AUTOLOAD" in source)
    environment = dict(os.environ)
    environment["PYTEST_ADDOPTS"] = "--deliberately-invalid-ambient-option"
    environment["TMPDIR"] = str(tmp_path)
    result = subprocess.run(
        [sys.executable, "-c", source],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "3 passed" in result.stdout
    assert "PytestCacheWarning" not in result.stdout + result.stderr
    assert not list(tmp_path.glob("day58-project-*"))
