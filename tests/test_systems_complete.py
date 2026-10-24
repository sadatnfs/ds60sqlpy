"""C++ content and real compiler evidence; other systems tracks remain independent."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / "courses" / "cpp"
NEW_IDS = [f"cpp-{number:03d}" for number in range(4, 43) if number != 9]


def compiler() -> str:
    result = shutil.which("clang++") or shutil.which("g++")
    if result is None:
        pytest.skip("C++ host compiler unavailable; Docker qualification is separate")
    return result


def compile_source(source: Path, executable: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            compiler(),
            "-std=c++20",
            "-O0",
            "-Wall",
            "-Wextra",
            "-Wconversion",
            "-Wpedantic",
            "-pthread",
            str(source),
            "-o",
            str(executable),
        ],
        capture_output=True,
        text=True,
        timeout=45,
    )


def test_cpp_all_planned_prerequisites_have_authored_content() -> None:
    plan = json.loads((ROOT / "docs/expansion/plans/cpp.json").read_text())["lessons"]
    records = json.loads((CPP / "lessons.json").read_text())["lessons"]
    ids = {record["id"] for record in records}
    assert ids == {lesson["id"] for lesson in plan}
    assert len(ids) == 42
    by_id = {record["id"]: record for record in records}
    for lesson in plan:
        guide = (ROOT / by_id[lesson["id"]]["guide_path"]).read_text()
        assert set(lesson["prerequisites"]) <= ids
        for prerequisite in lesson["prerequisites"]:
            assert f"`{prerequisite}`" in guide
        assert "compile and run tutorial" in guide
    assert by_id["cpp-009"]["verification_id"] == "cpp-ownership-v1"
    assert all(record["verification_id"] is None for record in records if record["id"] != "cpp-009")


@pytest.mark.parametrize("lesson_id", NEW_IDS)
def test_cpp_new_references_compile_and_run(tmp_path: Path, lesson_id: str) -> None:
    source = CPP / "solutions" / f"{lesson_id}_solution.cpp"
    executable = tmp_path / "reference"
    built = compile_source(source, executable)
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], cwd=tmp_path, capture_output=True, text=True, timeout=8)
    assert ran.returncode == 0, ran.stderr
    assert f"{lesson_id} examples passed\n" in ran.stdout
    assert not ran.stderr


@pytest.mark.parametrize("lesson_id", NEW_IDS)
def test_cpp_exercises_have_deterministic_topic_cases(lesson_id: str) -> None:
    fixture = json.loads((CPP / "fixtures" / f"{lesson_id}-cases.json").read_text())
    assert fixture["lesson_id"] == lesson_id
    assert [case["exercise"] for case in fixture["cases"]] == list(range(1, 7))
    assert len({case["input_or_change"] for case in fixture["cases"]}) == 6
    assert len({case["expected"] for case in fixture["cases"]}) == 6
    guide = (CPP / "guides" / f"{lesson_id}.md").read_text()
    assert "## Trace the mechanism" in guide
    assert len(re.findall(r"### Worked example [12]", guide)) == 2
    explanation = (CPP / "solutions" / f"{lesson_id}_solutions.md").read_text()
    assert len(re.findall(r"^## Exercise [1-6]:", explanation, re.MULTILINE)) == 6
    learner = (CPP / "lessons" / f"{lesson_id}.cpp").read_text()
    reference = (CPP / "solutions" / f"{lesson_id}_solution.cpp").read_text()
    assert reference != learner
    assert "Reference extension checks" in reference


@pytest.mark.parametrize(
    "lesson_id,original,broken",
    [
        ("cpp-006", "ec!=std::errc{} || ptr!=s.data()+s.size()", "ec!=std::errc{}"),
        ("cpp-014", "p!=s.data()+s.size()||n<0", "n<0"),
        ("cpp-028", "q!=s.data()+s.size()||id<0", "id<0"),
        ("cpp-040", "s.size()>16", "s.size()>17"),
    ],
)
def test_cpp_references_reject_plausible_contract_regressions(
    tmp_path: Path,
    lesson_id: str,
    original: str,
    broken: str,
) -> None:
    source = (CPP / "solutions" / f"{lesson_id}_solution.cpp").read_text()
    assert original in source
    attempt = tmp_path / "main.cpp"
    attempt.write_text(source.replace(original, broken, 1))
    executable = tmp_path / "regression"
    built = compile_source(attempt, executable)
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], cwd=tmp_path, capture_output=True, text=True, timeout=8)
    assert ran.returncode != 0, "A plausible contract defect was not rejected"


def test_cpp_multifile_link_success_and_missing_definition(tmp_path: Path) -> None:
    for source in (CPP / "fixtures/multifile").iterdir():
        shutil.copyfile(source, tmp_path / source.name)
    for stem in ("main", "math"):
        result = subprocess.run(
            [compiler(), "-std=c++20", "-c", f"{stem}.cpp", "-o", f"{stem}.o"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
    missing = subprocess.run(
        [compiler(), "main.o", "-o", "missing_definition"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert missing.returncode != 0
    assert "add" in missing.stdout + missing.stderr or "subtract" in missing.stdout + missing.stderr
    complete = subprocess.run(
        [compiler(), "main.o", "math.o", "-o", "complete"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert complete.returncode == 0, complete.stderr
    run = subprocess.run(
        [str(tmp_path / "complete")], cwd=tmp_path, capture_output=True, text=True, timeout=5
    )
    assert run.returncode == 0
    assert run.stdout == "add=5 subtract=2\n"
    duplicate = subprocess.run(
        [compiler(), "main.o", "math.o", "math.o", "-o", "duplicate"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert duplicate.returncode != 0


def test_cpp_tutorial_names_actual_execution_boundaries() -> None:
    tutorial = (CPP / "compile-and-run.md").read_text()
    for fact in (
        "main.cpp",
        "main.cpp.txt",
        "-std=c++20",
        "-pthread",
        "$LASTEXITCODE",
        "compile_status=$?",
        "-c main.cpp",
        "CMake",
        "Docker",
        "one C++ file",
        "stderr",
        "exit",
        "stale",
    ):
        assert fact in tutorial
    assert "\u2014" not in tutorial


def test_cpp_capstone_cli_preserves_input_and_failure_contracts(tmp_path: Path) -> None:
    executable = tmp_path / "analyzer"
    built = compile_source(CPP / "solutions/cpp-014_solution.cpp", executable)
    assert built.returncode == 0, built.stderr
    input_file = tmp_path / "readings.txt"
    input_file.write_text("10\n0\nbad\n-2\n25\n")
    result = subprocess.run(
        [str(executable), "--input", str(input_file)], capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 0
    assert result.stdout == "accepted=3 rejected=2 total=35\n"
    assert input_file.read_text() == "10\n0\nbad\n-2\n25\n"
    missing = subprocess.run(
        [str(executable), "--input", str(tmp_path / "missing.txt")],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert missing.returncode == 2
    assert not missing.stdout
    assert "cannot open" in missing.stderr
    input_file.write_text("1\n" * 101)
    excess = subprocess.run(
        [str(executable), "--input", str(input_file)], capture_output=True, text=True, timeout=5
    )
    assert excess.returncode == 2
    assert "budget exceeded" in excess.stderr
    input_file.write_text("")
    empty = subprocess.run(
        [str(executable), "--input", str(input_file)], capture_output=True, text=True, timeout=5
    )
    assert empty.returncode == 0
    assert empty.stdout == "accepted=0 rejected=0 total=0\n"


def test_cpp_record_library_has_separate_compilation_and_consumer(tmp_path: Path) -> None:
    fixture = CPP / "fixtures/record-library"
    for stem in ("record", "consumer"):
        result = subprocess.run(
            [
                compiler(),
                "-std=c++20",
                "-I",
                str(fixture),
                "-c",
                str(fixture / f"{stem}.cpp"),
                "-o",
                str(tmp_path / f"{stem}.o"),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
    executable = tmp_path / "consumer"
    linked = subprocess.run(
        [
            compiler(),
            str(tmp_path / "record.o"),
            str(tmp_path / "consumer.o"),
            "-o",
            str(executable),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert linked.returncode == 0, linked.stderr
    result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=5)
    assert result.returncode == 0
    assert result.stdout == "accepted=2 rejected=2\n"
