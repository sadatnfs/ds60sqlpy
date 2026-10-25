"""Copy-runnable C++ guide programs with actual compiler, output and parity evidence."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.source_format_parity import code_tokens

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/cpp"
EXPECTED = json.loads((BASE / "authoring/depth/expected_outputs.json").read_text())
PROGRAMS = sorted(EXPECTED)
IDS = sorted({name[:7] for name in PROGRAMS})


@pytest.mark.parametrize("name", PROGRAMS)
def test_complete_example_compiles_and_matches_documented_output(tmp_path: Path, name: str) -> None:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        pytest.skip("No prepared native compiler; Docker qualification is separate")
    source = BASE / "examples" / name
    executable = tmp_path / "example"
    built = subprocess.run(
        [
            compiler,
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
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], cwd=tmp_path, capture_output=True, text=True, timeout=8)
    assert ran.returncode == 0 and not ran.stderr, ran.stderr
    assert ran.stdout == EXPECTED[name]


@pytest.mark.parametrize("key", IDS)
def test_guide_embeds_two_complete_sources_and_specific_depth(key: str) -> None:
    text = (BASE / f"guides/{key}.md").read_text()
    assert "<!-- depth:start -->" in text
    assert "Record the concrete output, assertion" not in text
    assert "First identify the changed input. Then trace" not in text
    assert "Authored beta content" not in text
    examples = re.findall(r"```cpp\n(.*?)\n```", text, re.S)
    for index in (1, 2):
        name = f"{key}-example-{index}.cpp"
        source = (BASE / "examples" / name).read_text().rstrip()
        assert any(code_tokens(source) == code_tokens(example) for example in examples)
        assert source.count("int main(") == 1
        assert "#include" in source
        assert EXPECTED[name].rstrip() in text
    mechanism = re.search(r"<!-- depth:start -->(.*?)<!-- depth:end -->", text, re.S)
    assert mechanism and len(mechanism.group(1).split()) >= 250
    assert len(re.findall(r"^### Exercise [1-6]:", text, re.M)) == 6


def test_assert_configuration_example_has_distinct_release_observation(tmp_path: Path) -> None:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        pytest.skip("No prepared native compiler")
    executable = tmp_path / "release-example"
    subprocess.run(
        [
            compiler,
            "-std=c++20",
            "-DNDEBUG",
            str(BASE / "examples/cpp-013-example-2.cpp"),
            "-o",
            str(executable),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=45,
    )
    result = subprocess.run(
        [str(executable)], capture_output=True, text=True, check=True, timeout=8
    )
    assert result.stdout == "assert removed: evaluations=0\ncpp-013 example 2 checks passed\n"


def test_docker_project_guide_has_real_install_targets_and_scoped_persistent_mounts() -> None:
    guide = (BASE / "compile-and-run.md").read_text()
    for fragment in (
        "Docker-only CMake project route",
        "ds60sqlpy-worker-cpp20:0.4.0",
        "--network none",
        "--pull never",
        "--entrypoint",
        "--mount",
        "--prefix /project/install",
        "LastTest.log",
        "Invoke-CppTool",
        "cpp_tool",
        "without commas",
    ):
        assert fragment in guide
    assert "docker.sock" not in guide
    for fixture in ("multifile", "record-library"):
        cmake = (BASE / "fixtures" / fixture / "CMakeLists.txt").read_text()
        assert re.search(r"(?m)^\s*install\s*\(\s*TARGETS\b", cmake)
        assert re.search(r"(?m)^\s*install\s*\(\s*EXPORT\b", cmake)
        assert "INSTALL_INTERFACE:include" in cmake
