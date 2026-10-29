"""Owned Python web source and executable reference contracts."""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses/python-web"
UNITS = json.loads((COURSE / "authoring/units.json").read_text())


def test_complete_branch_prerequisites_and_sources() -> None:
    assert [unit["id"] for unit in UNITS] == [f"pyweb-{number:03}" for number in range(1, 73)]
    known = {unit["id"] for unit in UNITS}
    for unit in UNITS:
        for prerequisite in unit["prerequisites"]:
            if prerequisite.startswith("pyweb-"):
                assert prerequisite in known
                assert prerequisite < unit["id"]
        text = (COURSE / "authoring/chapters" / (unit["id"] + ".md")).read_text()
        assert len(text.split()) >= 500
        assert text.count("## Worked case") >= 2
        assert "\u2014" not in text
        source = COURSE / "authoring/programs" / (unit["id"] + unit["suffix"])
        if unit["language"] == "python":
            ast.parse(source.read_text(), feature_version=(3, 11))
            assert unit["runtime"] == "python-web"
        else:
            assert unit["id"] in {"pyweb-068", "pyweb-070", "pyweb-072"}
            assert unit["runtime"] == "reading"
    # Framework entrypoints can follow the shared foundation independently.
    for identifier in ("pyweb-013", "pyweb-027", "pyweb-045"):
        assert "pyweb-012" in next(u for u in UNITS if u["id"] == identifier)["prerequisites"]


def test_generated_outputs_are_exact_durable_source_projection() -> None:
    path = COURSE / "authoring/build.py"
    spec = importlib.util.spec_from_file_location("web_authoring_build", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for output, expected in module.outputs().items():
        assert output.read_text() == expected, str(output.relative_to(ROOT))


def test_no_pad_starts_a_persistent_http_server() -> None:
    forbidden = {"serve_forever", "runserver", "uvicorn.run", "app.run", "run_simple"}
    for unit in UNITS:
        if unit["language"] != "python":
            continue
        source = COURSE / "authoring/programs" / (unit["id"] + ".py")
        tree = ast.parse(source.read_text())
        calls = {ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)}
        assert not any(call in forbidden or call.endswith(".serve_forever") for call in calls)
        assert '__name__ == "__main__"' in source.read_text()
    assert (
        "pyweb-001: all reference checks passed" in (COURSE / "examples/pyweb-001.py").read_text()
    )


@pytest.mark.parametrize(
    "unit", [unit for unit in UNITS if unit["language"] == "python"], ids=lambda unit: unit["id"]
)
def test_real_finite_program_in_explicit_prepared_interpreter(unit: dict[str, Any]) -> None:
    interpreter = os.environ.get("DS60_PYTHON_WEB_INTERPRETER")
    if not interpreter:
        pytest.skip(
            "Needs the explicitly prepared Python-web interpreter; source checks are separate"
        )
    result = subprocess.run(
        [interpreter, str(COURSE / "examples" / (unit["id"] + ".py"))],
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip(), unit["id"]


def test_project_links_resolve_from_authored_and_published_locations() -> None:
    for identifier in ("pyweb-068", "pyweb-070", "pyweb-072"):
        for directory in ("authoring/programs", "examples", "guides"):
            source = COURSE / directory / (identifier + ".md")
            project_links = [
                target
                for target in re.findall(r"\]\(([^)]+)\)", source.read_text())
                if "projects/web-lab/README.md" in target
            ]
            assert project_links, source
            for target in project_links:
                assert (source.parent / target).resolve() == COURSE / "projects/web-lab/README.md"
                assert (source.parent / target).is_file()
