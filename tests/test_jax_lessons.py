"""JAX teaching contracts and explicit opt-in fresh-process numerical checks."""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/jax"
PLAN = json.loads((BASE / "track.json").read_text(encoding="utf-8"))["lessons"]
ENTRIES = json.loads((BASE / "lessons.json").read_text(encoding="utf-8"))["lessons"]
RUNNABLE = [entry for entry in ENTRIES if entry["runtime_profile"] == "jax-cpu"]
READING = [entry for entry in ENTRIES if entry["runtime_profile"] == "reading"]
JAX_ENABLED = os.environ.get("DS60_TEST_JAX") == "1" and importlib.util.find_spec("jax") is not None


def main_has_numerical_check(tree: ast.Module) -> bool:
    main = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    return any(
        isinstance(node, ast.Assert)
        or (
            isinstance(node, ast.Raise)
            and isinstance(node.exc, ast.Call)
            and isinstance(node.exc.func, ast.Name)
            and node.exc.func.id == "AssertionError"
        )
        or (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"close", "compare"}
        )
        for node in ast.walk(main)
    )


def test_complete_route_preserves_the_planned_capability_sequence() -> None:
    identifiers = [entry["id"] for entry in ENTRIES]
    assert identifiers == [f"jax-{number:03d}" for number in range(1, 35)]
    assert [row["id"] for row in PLAN] == identifiers
    assert len(RUNNABLE) == 31 and len(READING) == 3
    assert {row["level"] for row in PLAN} == {"beginner", "intermediate", "advanced"}
    seen: set[str] = set()
    for row, entry in zip(PLAN, ENTRIES, strict=True):
        assert set(row["prerequisites"]) <= seen
        assert row["runtime"] == entry["runtime_profile"]
        assert entry["verification_id"] is None
        assert row["concepts"] and row["outcome"] and row["verification"]
        seen.add(row["id"])


@pytest.mark.parametrize("entry", ENTRIES, ids=lambda entry: entry["id"])
def test_each_unit_has_distinct_worked_and_independent_cases(entry: dict[str, Any]) -> None:
    guide = (ROOT / entry["guide_path"]).read_text(encoding="utf-8")
    assert len(guide.split()) >= 1000
    assert re.findall(r"^### Worked example ([12]):", guide, re.M) == ["1", "2"]
    assert re.findall(r"^### Exercise ([1-6]):", guide, re.M) == list("123456")
    titles = re.findall(r"^### Exercise [1-6]: (.+)$", guide, re.M)
    assert len(set(titles)) == 6
    for heading in (
        "## Mechanism and purpose",
        "## Derivation and shape contract",
        "## Diagnosis and boundaries",
        "## Transfer and review",
        "## Primary references",
        "## Ask an AI tutor about this lesson",
    ):
        assert heading in guide
    assert "$guide-ds60sqlpy-learning" in guide
    assert "\u2014" not in guide
    explanation = (ROOT / entry["solution_paths"][-1]).read_text(encoding="utf-8")
    assert re.findall(r"^## Exercise ([1-6]):", explanation, re.M) == list("123456")
    assert "## Scope of this evidence" in explanation
    if entry["runtime_profile"] == "reading":
        assert entry["language"] == "markdown"
        assert "This unit uses written traces" in guide
        assert "```python" not in guide
    else:
        assert entry["language"] == "python"
        blocks = re.findall(r"```python\n(.*?)\n```", guide, re.S)
        assert len(blocks) == 2
        for block in blocks:
            tree = ast.parse(block)
            assert 'if __name__ == "__main__":' in block
            assert main_has_numerical_check(tree)


@pytest.mark.parametrize("entry", RUNNABLE, ids=lambda entry: entry["id"])
def test_runnable_sources_are_complete_and_do_not_acquire_dependencies(
    entry: dict[str, Any],
) -> None:
    reference = (ROOT / entry["solution_paths"][0]).read_text(encoding="utf-8")
    learner = (ROOT / entry["source_path"]).read_text(encoding="utf-8")
    tree = ast.parse(reference)
    assert 'if __name__ == "__main__":' in reference
    assert len(re.findall(r"# Case [1-8]:", reference)) == 8
    assert main_has_numerical_check(tree)
    assert re.findall(r"# Exercise ([1-6]):", learner) == list("123456")
    assert learner.count("raise NotImplementedError") == 6
    assert reference != learner
    allowed = {"__future__", "math", "numpy", "jax", "tempfile", "pathlib", "time"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name.split(".")[0] in allowed for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.module and node.module.split(".")[0] in allowed
    assert 'jax.config.update("jax_enable_x64", True)' in reference
    assert "pip install" not in reference and "http://" not in reference


@pytest.mark.skipif(
    importlib.util.find_spec("ruff") is None, reason="Requires the prepared authoring formatter"
)
def test_subject_generation_is_exact_without_running_jax() -> None:
    completed = subprocess.run(
        [sys.executable, "-B", str(BASE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.xdist_group("jax-runtime")
@pytest.mark.skipif(not JAX_ENABLED, reason="Requires explicitly prepared JAX 0.12.0.1 CPU runtime")
@pytest.mark.parametrize("entry", RUNNABLE, ids=lambda entry: entry["id"])
def test_reference_in_a_fresh_cpu_process(entry: dict[str, Any]) -> None:
    environment = dict(os.environ)
    environment.update(
        JAX_PLATFORMS="cpu",
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUNBUFFERED="1",
        OMP_NUM_THREADS="2",
        OPENBLAS_NUM_THREADS="2",
    )
    completed = subprocess.run(
        [sys.executable, "-B", str(ROOT / entry["solution_paths"][0])],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
        env=environment,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert f"{entry['id']}: 8 asserted cases passed" in completed.stdout


@pytest.mark.xdist_group("jax-runtime")
@pytest.mark.skipif(not JAX_ENABLED, reason="Requires explicitly prepared JAX 0.12.0.1 CPU runtime")
def test_runtime_version_matches_the_authored_api_contract() -> None:
    jax = import_module("jax")
    jaxlib = import_module("jaxlib")

    assert jax.__version__ == "0.12.0.1"
    assert jaxlib.__version__ == "0.12.0.1"
    assert jax.default_backend() == "cpu"
