"""Evidence checks for the durable systems lessons, separate from runtime qualification."""

from __future__ import annotations

import ast
import json
import re
import runpy
import shutil
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest

from ds60sqlpy.checks import _markdown_link_text

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "cpp": {"cpp-001", "cpp-002", "cpp-003", "cpp-009"},
    "scala-spark": {"spark-001", "spark-002", "spark-003", "spark-013"},
    "kubernetes": {"k8s-001", "k8s-002", "k8s-003", "k8s-008"},
}


def _lessons(track: str) -> list[dict[str, Any]]:
    payload = json.loads((ROOT / "courses" / track / "lessons.json").read_text())
    assert payload["schema_version"] == 1
    assert payload["track_id"] == track
    records = payload["lessons"]
    assert isinstance(records, list) and all(isinstance(item, dict) for item in records)
    return cast(list[dict[str, Any]], records)


@pytest.mark.parametrize("track", EXPECTED)
def test_authored_metadata_has_complete_separate_files(track: str) -> None:
    records = _lessons(track)
    assert EXPECTED[track] <= {item["id"] for item in records}
    assert len(records) == len({item["id"] for item in records})
    for item in records:
        assert item["status"] == "authored"
        assert item["verification_id"] in (
            None,
            "cpp-ownership-v1",
            "spark-rows-v1",
            "k8s-readiness-v1",
            "k8s-readiness-v1",
        )
        paths = [item["guide_path"], item["source_path"], *item["solution_paths"]]
        assert len(paths) == len(set(paths))
        for relative in paths:
            path = ROOT / relative
            assert path.is_file(), relative
            assert path.resolve().is_relative_to(ROOT / "courses" / track)
            assert "\u2014" not in path.read_text(), relative
        assert any(path.endswith("_solutions.md") for path in item["solution_paths"])
        if item["language"] != "markdown":
            assert len(item["solution_paths"]) >= 2


@pytest.mark.parametrize("track", EXPECTED)
def test_guides_have_real_teaching_steps_and_six_distinct_tasks(track: str) -> None:
    for item in _lessons(track):
        guide = (ROOT / item["guide_path"]).read_text()
        for heading in (
            "Level and prerequisites",
            "Learning objectives",
            "Vocabulary and concepts",
            "Worked example / walkthrough",
            "Exercises",
            "Self-check",
            "Common pitfalls",
            "Next step",
            "Ask Codex about this lesson",
        ):
            assert f"## {heading}" in guide, (item["id"], heading)
        assert guide.rfind("## Ask Codex about this lesson") > guide.rfind("## Next step")
        assert "$guide-ds60sqlpy-learning" in guide
        assert item["guide_path"] in guide
        assert item["source_path"] in guide
        assert "solutions/" in guide
        numbers = re.findall(r"^### Exercise ([1-6]):", guide, re.M)
        assert set(numbers) == set("123456"), item["id"]
        assert len(numbers) == 6, item["id"]
        assert len(re.findall(r"\*\*Expected(?: result/shape)?:\*\*", guide)) >= 6
        assert len(re.findall(r"\*\*Verify:\*\*", guide)) >= 6
        learner = (ROOT / item["source_path"]).read_text()
        assert {str(n) for n in range(1, 7)} <= set(re.findall(r"Exercise ([1-6]):", learner))


@pytest.mark.parametrize("track", EXPECTED)
def test_system_lesson_links_stay_inside_real_authored_tree(track: str) -> None:
    for path in (ROOT / "courses" / track).rglob("*.md"):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", _markdown_link_text(path.read_text())):
            if target.startswith(("https://", "http://", "#")):
                continue
            relative = target.split("#", 1)[0]
            assert (path.parent / relative).exists(), (path.relative_to(ROOT), target)


def test_spark_local_oracle_matches_shared_fixture_without_spark() -> None:
    fixture = json.loads((ROOT / "courses/scala-spark/fixtures/spark013.json").read_text())
    reference = runpy.run_path(str(ROOT / "courses/scala-spark/fixtures/spark013_oracle.py"))
    assert fixture["rows"] == [list(row) for row in reference["fixture"]]
    assert fixture["expected_summary"] == [list(row) for row in reference["golden"]]
    assert reference["reference_metrics"](reference["paid_fixture"]) == (6, 4, 250)
    for path in (ROOT / "courses/scala-spark").rglob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    for relative in ("lessons/spark-013.py", "solutions/spark-013_solution.py"):
        text = (ROOT / "courses/scala-spark" / relative).read_text()
        assert "def paid_events(raw)" in text
        assert "def summarize(" in text
        assert 'if __name__ == "__main__"' in text


def test_kubernetes_sources_use_the_offline_owned_fixture() -> None:
    yaml = pytest.importorskip("yaml")
    for path in (ROOT / "courses/kubernetes").rglob("*.yaml"):
        for doc in yaml.safe_load_all(path.read_text()):
            if not doc:
                continue
            assert "namespace" not in doc["metadata"]
            assert doc["kind"] in {"Deployment", "Service", "Job"}
            if doc["kind"] in {"Deployment", "Job"}:
                pod = doc["spec"]["template"]["spec"]
                assert pod["automountServiceAccountToken"] is False
                for container in pod["containers"]:
                    assert container["image"] == "ds60sqlpy-k8s-fixture:0.2.0"
                    assert container["imagePullPolicy"] == "Never"
                    assert container["securityContext"]["allowPrivilegeEscalation"] is False
                    assert container["securityContext"]["readOnlyRootFilesystem"] is True
    learner = (ROOT / "courses/kubernetes/lessons/k8s-008.yaml").read_text()
    docs = list(yaml.safe_load_all(learner))
    assert [doc["metadata"]["name"] for doc in docs] == ["hello", "hello"]


@pytest.mark.parametrize("filename", ["cpp-002_solution.cpp", "cpp-003_solution.cpp"])
def test_native_cpp_small_references(tmp_path: Path, filename: str) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("native clang++ is optional; image qualification is a separate proof")
    executable = tmp_path / "reference"
    compile_result = subprocess.run(
        [
            compiler,
            "-std=c++20",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            str(ROOT / "courses/cpp/solutions" / filename),
            "-o",
            str(executable),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
    if filename.startswith("cpp-002"):
        assert result.stdout == "hello, learner\n"
    else:
        assert "whole=3 fractional=3.5 promoted=3.5 late=3\n" in result.stdout
        assert "wide=10000000000; cents=200\n" in result.stdout


@pytest.mark.parametrize("variant", ["reference", "learner-stub", "drops-zero"])
def test_cpp_typed_harness_rejects_real_misconceptions(tmp_path: Path, variant: str) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("native clang++ is optional; image qualification is separate")
    original = ROOT / (
        "courses/cpp/lessons/cpp-009.cpp"
        if variant == "learner-stub"
        else "courses/cpp/solutions/cpp-009_solution.cpp"
    )
    source = original.read_text()
    if variant == "drops-zero":
        assert "value >= 0" in source
        source = source.replace("value >= 0", "value > 0")
    attempt = tmp_path / "main.cpp"
    attempt.write_text(source)
    obj = tmp_path / "learner.o"
    harness = ROOT / "courses/cpp/fixtures/cpp-ownership-v1.cpp"
    compile_result = subprocess.run(
        [compiler, "-std=c++20", "-Dmain=ds60_learner_main", "-c", str(attempt), "-o", str(obj)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    exe = tmp_path / "checks"
    link_result = subprocess.run(
        [compiler, "-std=c++20", str(harness), str(obj), "-o", str(exe)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert link_result.returncode == 0, link_result.stderr
    result = subprocess.run([str(exe)], cwd=tmp_path, capture_output=True, text=True, timeout=5)
    receipt = json.loads((tmp_path / "checks.json").read_text())
    assert receipt["checks"]
    assert all(type(check["passed"]) is bool for check in receipt["checks"])
    if variant == "reference":
        assert result.returncode == 0, result.stderr
        assert len(receipt["checks"]) == 14
        assert all(check["passed"] for check in receipt["checks"])
    else:
        assert result.returncode != 0
        assert any(not check["passed"] for check in receipt["checks"])


def test_pyspark_variant_has_separate_source_with_same_typed_fixture_contract() -> None:
    pilot = next(item for item in _lessons("scala-spark") if item["id"] == "spark-013")
    assert pilot["verification_id"] == "spark-rows-v1"
    assert len(pilot["variants"]) == 1
    variant = pilot["variants"][0]
    assert variant["id"] == "pyspark"
    assert variant["language"] == "python"
    assert variant["runtime_profile"] == "spark-local-python"
    assert variant["verification_id"] == "spark-rows-v1"
    assert variant["source_path"] != pilot["source_path"]
    assert (ROOT / variant["source_path"]).is_file()
    assert all((ROOT / path).is_file() for path in variant["solution_paths"])
    assert "courses/scala-spark/solutions/spark-013_solutions.md" in variant["solution_paths"]
