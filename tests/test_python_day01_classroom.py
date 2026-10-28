"""Day 1 source, notebook, actual execution, and fresh-process regressions."""

from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import nbformat
import pytest

from ds60sqlpy.catalog import Catalog
from scripts.audit_lesson_depth import measure_lesson
from scripts.audit_practice import count_practice

ROOT = Path(__file__).resolve().parents[1]
LEARNER = Path("python/ds-60day/notebooks/day01_setup_and_repl.ipynb")
GUIDE = Path("python/ds-60day/companion-guides/day01_setup_and_repl.md")
REFERENCE = Path("python/ds-60day/solutions/day01_setup_and_repl/day01_solutions.ipynb")
EXPLAINED = Path("python/ds-60day/solutions/day01_setup_and_repl/day01_solutions.md")
read_notebook: Callable[..., nbformat.NotebookNode] = nbformat.read


def notebook(relative: Path) -> nbformat.NotebookNode:
    return read_notebook(ROOT / relative, as_version=4)


def code_for_task(number: int) -> str:
    return next(
        str(cell.source)
        for cell in notebook(REFERENCE).cells
        if cell.cell_type == "code" and f"exercise-{number:02d}" in cell.metadata.get("tags", [])
    )


def child(tmp_path: Path, source: str, name: str) -> subprocess.CompletedProcess[str]:
    directory = tmp_path / name
    directory.mkdir()
    program = directory / "main.py"
    program.write_text(source, encoding="utf-8")
    runtime = directory / "private-runtime"
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + str(ROOT)
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; import sys; "
            "from ds60sqlpy.notebook_execution import execute_python_file; "
            "raise SystemExit(execute_python_file(Path(sys.argv[1]), Path(sys.argv[2])))",
            str(program),
            str(runtime),
        ],
        cwd=directory,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.mark.parametrize("relative", [LEARNER, REFERENCE])
def test_day01_notebooks_are_valid_clean_and_keep_deterministic_cell_ids(relative: Path) -> None:
    value = notebook(relative)
    nbformat.validate(value)
    assert value.nbformat_minor == 5
    assert value.metadata.kernelspec == {
        "display_name": "Python (ds60sqlpy)",
        "language": "python",
        "name": "ds60sqlpy",
    }
    assert value.metadata.course.lesson_id == "python-01"
    assert value.metadata.course.day == 1 and value.metadata.course.track == "python"
    assert value.metadata.course.artifact == ("learner" if relative == LEARNER else "solution")
    identifiers = set()
    for index, cell in enumerate(value.cells):
        identity = f"{relative.as_posix()}:{index}:{cell.cell_type}".encode()
        expected = "ds60-" + hashlib.sha256(identity).hexdigest()[:16]
        assert cell.id == expected and cell.id not in identifiers
        identifiers.add(cell.id)
        assert "\u2014" not in cell.source
        if cell.cell_type == "code":
            assert cell.execution_count is None and cell.outputs == []


def test_day01_ten_practice_contracts_and_depth_match_all_surfaces() -> None:
    catalog = Catalog.load(ROOT)
    lesson = catalog.get("python-01")
    assert list(lesson.prerequisites) == []
    assert lesson.day == 1
    assert not measure_lesson(catalog, lesson).issues
    for relative in (LEARNER, GUIDE, REFERENCE, EXPLAINED):
        assert count_practice(ROOT / relative, solution="solutions/" in str(relative)) == 10
    learner_prompts = [
        cell.source
        for cell in notebook(LEARNER).cells
        if cell.cell_type == "markdown" and cell.source.startswith("### Exercise ")
    ]
    solved_prompts = [
        cell.source
        for cell in notebook(REFERENCE).cells
        if cell.cell_type == "markdown" and cell.source.startswith("## Exercise ")
    ]
    guide = (ROOT / GUIDE).read_text()
    explained = (ROOT / EXPLAINED).read_text()
    assert len(learner_prompts) == len(solved_prompts) == 10
    for number, (prompt, solved) in enumerate(zip(learner_prompts, solved_prompts, strict=True), 1):
        title = prompt.splitlines()[0].removeprefix(f"### Exercise {number}: ")
        assert solved.startswith(f"## Exercise {number}: {title}\n")
        assert f"### Exercise {number}: {title}\n" in guide
        assert f"## Exercise {number}: {title}\n" in explained


def test_browser_workflow_precedes_optional_host_tools_and_links_resolve() -> None:
    guide = (ROOT / GUIDE).read_text()
    assert re.search(r"^##\s+How to run this lesson", guide, flags=re.M)
    assert guide.index("## How to run") < guide.index("## Level and prerequisites")
    assert (
        "host Python, virtual environments, VS Code, pip, and\nJupyter are not prerequisites"
        in guide
    )
    assert "### Optional contributor REPL and Jupyter route" in guide
    required = guide.split("### Optional contributor REPL and Jupyter route")[0]
    for forbidden in ("pip install ", "python -m venv", "PowerShell", "Install Python"):
        assert forbidden not in required
    assert guide.rstrip().endswith("```")
    assert "## Ask an AI tutor about this lesson" in guide
    assert "$guide-ds60sqlpy-learning" in guide
    for relative in (GUIDE, EXPLAINED):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", (ROOT / relative).read_text()):
            if not target.startswith(("https://", "http://", "#")):
                assert (ROOT / relative).parent.joinpath(target.split("#")[0]).resolve().is_file()


def test_default_day01_code_imports_only_standard_library_and_installs_nothing() -> None:
    for relative in (LEARNER, REFERENCE):
        for cell in notebook(relative).cells:
            if cell.cell_type != "code":
                continue
            tree = ast.parse(cell.source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    assert {alias.name.split(".")[0] for alias in node.names} <= {
                        "platform",
                        "sys",
                        "pathlib",
                        "importlib",
                    }
                if isinstance(node, ast.ImportFrom):
                    assert node.module is not None
                    assert node.module.split(".")[0] in {"platform", "sys", "pathlib", "importlib"}
            for command in (
                "pip install",
                "venv.create",
                "os.system",
                "subprocess.",
                "docker.sock",
                "ensurepip",
            ):
                assert command not in cell.source


@pytest.mark.parametrize("relative", [LEARNER, REFERENCE])
def test_complete_notebook_code_executes_in_actual_notebook_adapter(
    tmp_path: Path, relative: Path
) -> None:
    code = "\n\n".join(
        "# %%\n" + str(cell.source) for cell in notebook(relative).cells if cell.cell_type == "code"
    )
    result = child(tmp_path, code, "notebook-code")
    assert result.returncode == 0, result.stdout + result.stderr
    if relative == LEARNER:
        for expected in (
            "Python reads source text.",
            "Python:",
            "Implementation:",
            "Interpreter:",
            "Working directory:",
            "Total: 36",
            "Ready",
        ):
            assert expected in result.stdout
    else:
        for expected in (
            "marker: amber",
            "repeat: 42",
            "math: True",
            "intentionally absent: False",
            "Hello",
        ):
            assert expected in result.stdout
        assert "not a measurement of this device" in result.stdout


def test_identity_report_is_actual_child_interpreter_and_directory(tmp_path: Path) -> None:
    code = next(
        cell.source
        for cell in notebook(LEARNER).cells
        if "identity" in cell.metadata.get("tags", [])
    )
    result = child(tmp_path, code, "identity")
    assert result.returncode == 0, result.stderr
    fields = dict(line.split(": ", 1) for line in result.stdout.splitlines())
    assert set(fields) == {"Python", "Implementation", "Interpreter", "Working directory"}
    assert fields["Python"].startswith(("3.11.", "3.12."))
    assert fields["Implementation"]
    assert Path(fields["Interpreter"]).resolve() == Path(sys.executable).resolve()
    assert Path(fields["Working directory"]).resolve() == (tmp_path / "identity").resolve()


def test_marked_last_expression_and_plain_script_have_distinct_real_outputs(tmp_path: Path) -> None:
    marked = child(tmp_path, '# %%\nprint("before")\n7 * 6\n', "marked")
    plain = child(tmp_path, 'print("before")\n7 * 6\n', "plain")
    explicit = child(tmp_path, 'print("before")\nprint(7 * 6)\n', "explicit")
    assert marked.returncode == plain.returncode == explicit.returncode == 0
    assert "before" in marked.stdout and re.search(r"Out\[\d+\]:\s*42", marked.stdout)
    assert plain.stdout == "before\n"
    assert explicit.stdout == "before\n42\n"


def test_two_fresh_runs_forget_variables_while_cells_in_one_run_share_them(tmp_path: Path) -> None:
    namespace: dict[str, Any] = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(code_for_task(4), "day01-task4-reference", "exec"), namespace)
    first = child(tmp_path, namespace["run_a_source"], "run-a")
    second = child(tmp_path, namespace["run_b_source"], "run-b")
    repaired = child(tmp_path, namespace["run_c_source"], "run-c")
    combined = child(tmp_path, '# %%\nvisit = "north"\n# %%\nprint(visit)\n', "same-run-two-cells")
    assert first.returncode == repaired.returncode == combined.returncode == 0
    assert first.stdout == combined.stdout == "north\n"
    assert repaired.stdout == "south\n"
    assert second.returncode != 0
    assert "NameError" in second.stdout + second.stderr
    assert "name 'visit' is not defined" in second.stdout + second.stderr
    assert json.loads((tmp_path / "run-b/private-runtime/execution.json").read_text()) == {
        "error_line": 2
    }


def test_missing_name_error_and_repair_are_real_separate_executions(tmp_path: Path) -> None:
    broken = child(tmp_path, "print(greeting)\n", "broken")
    wrong_case = child(tmp_path, 'Print("Hello")\n', "wrong-case")
    repaired = child(tmp_path, code_for_task(7), "repaired")
    assert broken.returncode != 0 and wrong_case.returncode != 0
    assert "NameError: name 'greeting' is not defined" in broken.stderr
    assert "NameError: name 'Print' is not defined" in wrong_case.stderr
    assert repaired.returncode == 0 and repaired.stdout == "Hello\n"
    assert json.loads((tmp_path / "broken/private-runtime/execution.json").read_text()) == {
        "error_line": 1
    }


def test_repeated_saved_program_content_matches_across_processes(tmp_path: Path) -> None:
    source = code_for_task(9)
    first = child(tmp_path, source, "repeat-a")
    second = child(tmp_path, source, "repeat-b")
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout == "repeat: 42\n"
    assert (tmp_path / "repeat-a/main.py").read_bytes() == (
        tmp_path / "repeat-b/main.py"
    ).read_bytes()


def test_marked_notebook_display_stops_on_error_before_later_cells(tmp_path: Path) -> None:
    result = child(
        tmp_path,
        '# %%\nprint("first")\n# %%\nprint(greeting)\n# %%\nprint("SHOULD NOT RUN")\n',
        "stop-on-first-error",
    )
    assert result.returncode != 0
    assert "first" in result.stdout and "NameError" in result.stdout + result.stderr
    assert "SHOULD NOT RUN" not in result.stdout
