"""Prove actual notebook semantics in fresh child interpreters, without servers."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ds60sqlpy.notebook_execution import PythonCell, python_cells

ROOT = Path(__file__).resolve().parents[1]


def child(
    tmp_path: Path, source: str, *, no_site: bool = False, prior_profile: Path | None = None
) -> tuple[subprocess.CompletedProcess[str], Path]:
    program = tmp_path / "submitted.py"
    program.write_text(source, encoding="utf-8")
    runtime = tmp_path / "private-runtime"
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "src")
    environment["MPLBACKEND"] = "Agg"
    environment["MPLCONFIGDIR"] = str(tmp_path / "matplotlib-cache")
    if prior_profile is not None:
        environment["IPYTHONDIR"] = str(prior_profile)
    command = [
        sys.executable,
        *(["-S"] if no_site else []),
        "-c",
        (
            "import sys; from pathlib import Path; "
            "from ds60sqlpy.notebook_execution import execute_python_file; "
            "raise SystemExit(execute_python_file(Path(sys.argv[1]), Path(sys.argv[2])))"
        ),
        str(program),
        str(runtime),
    ]
    result = subprocess.run(
        command, cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=25
    )
    return result, runtime


def test_real_top_level_markers_keep_offsets_and_preserve_cell_text() -> None:
    source = "import math\n# %% first\nvalue = 3\n\n#%%\nprint(value)\n"
    cells, interactive = python_cells(source)

    assert interactive
    assert cells == (
        PythonCell("import math\n", 1),
        PythonCell("value = 3\n\n", 3),
        PythonCell("print(value)\n", 6),
    )


@pytest.mark.parametrize("quote", ['"""', "'''"])
def test_strings_cannot_spoof_markers_or_magics(quote: str) -> None:
    source = f"text = {quote}\n# %%\n%timeit imaginary()\n%%sql\n{quote}\nprint(text)\n"
    cells, interactive = python_cells(source)

    assert interactive is False
    assert cells == (PythonCell(source, 1),)


@pytest.mark.parametrize(
    "source",
    [
        "result = (100\n% 7)\n",
        "result = 100 \\\n% 7\n",
        "result = 100 \\\n# %%\n7\n",
        "result = 100 % 7\n",
        'print("%timeit and # %%")\n',
        "x = [\n# %%\n1, 2]\n",
        "x = 1 # %%\n",
        "def example():\n    # %%\n    return 1\n",
    ],
)
def test_percent_operators_and_ordinary_comments_do_not_require_ipython(source: str) -> None:
    assert python_cells(source) == ((PythonCell(source, 1),), False)


@pytest.mark.parametrize(
    "source",
    ["%timeit -n1 -r1 pass\n", "timing = %timeit -o -n1 -r1 pass\n", "output = !echo hello\n"],
)
def test_line_magics_are_detected_including_assignment(source: str) -> None:
    assert python_cells(source)[1] is True


def test_cell_magic_body_is_opaque_and_verbatim() -> None:
    source = "# %%\n%%sql\nSELECT ('unbalanced SQL dollar quote $$;\n# %%\nprint(5)\n"
    cells, interactive = python_cells(source)

    assert interactive
    assert cells == (
        PythonCell("%%sql\nSELECT ('unbalanced SQL dollar quote $$;\n", 2),
        PythonCell("print(5)\n", 5),
    )


def test_plain_python_keeps_runpy_without_importing_optional_ipython(tmp_path: Path) -> None:
    result, runtime = child(
        tmp_path,
        "import sys\nassert 'IPython' not in sys.modules\n"
        "assert __name__ == '__main__'\nprint('plain success')\n",
        no_site=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "plain success"
    assert not runtime.exists()


def test_missing_ipython_reports_the_selected_backend_profile(tmp_path: Path) -> None:
    result, _ = child(tmp_path, "# %%\nprint(1)\n", no_site=True)

    assert result.returncode != 0
    assert "IPython" in result.stderr and "notebooks" in result.stderr
    assert "selected Python backend" in result.stderr


def test_cells_share_state_and_real_timeit_then_stop_with_normal_namespace(tmp_path: Path) -> None:
    pytest.importorskip("IPython")
    result, runtime = child(
        tmp_path,
        "# %%\nanswer = 40\n# %%\nanswer += 2\n"
        "%timeit -n1 -r1 answer + 1\nprint('shared', answer)\n"
        "assert __name__ == '__main__'\n",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "shared 42" in result.stdout and "per loop" in result.stdout
    assert not (runtime / "execution.json").exists()
    assert not list(runtime.rglob("*.sqlite"))
    assert not list(runtime.rglob("ipython_config.py"))


def test_custom_sql_cell_magic_receives_its_original_body(tmp_path: Path) -> None:
    pytest.importorskip("IPython")
    result, _ = child(
        tmp_path,
        "# %%\nfrom IPython.core.magic import register_cell_magic\n"
        "@register_cell_magic\ndef sql(line, cell):\n"
        "    assert line == 'local_fixture'\n"
        "    assert cell == \"SELECT 'kept';\\nSELECT 2;\\n\"\n"
        "    print('SQL BODY PRESERVED')\n"
        "# %%\n%%sql local_fixture\nSELECT 'kept';\nSELECT 2;\n"
        "# %%\nprint('following Python cell')\n",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "SQL BODY PRESERVED" in result.stdout
    assert "following Python cell" in result.stdout


@pytest.mark.parametrize(
    ("source", "line"),
    [
        (
            "# %%\nanswer = 40\n# %%\n\n\nanswer += 2\n"
            "raise ValueError('broken')\n# %%\nprint('LATER')\n",
            7,
        ),
        ("# %%\nanswer = 1\n# %%\n\n\nif True print('broken')\n# %%\nprint('LATER')\n", 6),
        (
            "# %%\ndef broken():\n    raise RuntimeError('earlier function')\n"
            "# %%\nbroken()\n# %%\nprint('LATER')\n",
            3,
        ),
    ],
)
def test_error_results_fail_stop_and_report_original_global_line(
    tmp_path: Path, source: str, line: int
) -> None:
    pytest.importorskip("IPython")
    result, runtime = child(tmp_path, source)

    assert result.returncode != 0
    assert "LATER" not in result.stdout
    assert json.loads((runtime / "execution.json").read_text()) == {"error_line": line}
    assert f"source line {line}" in result.stderr


@pytest.mark.parametrize("interactive", [False, True])
@pytest.mark.parametrize("code", [0, 7])
def test_system_exit_status_and_early_stop_are_respected(
    tmp_path: Path, interactive: bool, code: int
) -> None:
    if interactive:
        pytest.importorskip("IPython")
    source = ("# %%\n" if interactive else "") + f"raise SystemExit({code})\n"
    source += "# %%\nprint('SHOULD NOT RUN')\n" if interactive else "print('SHOULD NOT RUN')\n"
    result, _ = child(tmp_path, source)

    assert result.returncode == code
    assert "SHOULD NOT RUN" not in result.stdout


def test_profile_is_private_and_each_child_has_a_fresh_namespace(tmp_path: Path) -> None:
    pytest.importorskip("IPython")
    profile = tmp_path / "user-profile"
    startup = profile / "profile_default/startup"
    startup.mkdir(parents=True)
    (startup / "00-startup.py").write_text("raise RuntimeError('USER STARTUP RAN')\n")
    (profile / "ipython_config.py").write_text("raise RuntimeError('USER CONFIG RAN')\n")
    first, runtime = child(tmp_path, "# %%\nprivate_answer = 99\n", prior_profile=profile)
    second, _ = child(tmp_path, "# %%\nprint(private_answer)\n", prior_profile=profile)

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode != 0 and "NameError" in second.stdout
    assert "USER STARTUP RAN" not in first.stdout + first.stderr + second.stdout + second.stderr
    assert "USER CONFIG RAN" not in first.stdout + first.stderr + second.stdout + second.stderr
    assert not list(profile.rglob("*.sqlite"))
    assert (runtime / "ipython").is_dir()


def test_plain_error_preserves_exception_and_line_metadata(tmp_path: Path) -> None:
    result, runtime = child(tmp_path, "\n\nvalue = 3\nraise ValueError('plain failure')\n")

    assert result.returncode != 0 and "ValueError: plain failure" in result.stderr
    assert json.loads((runtime / "execution.json").read_text()) == {"error_line": 4}


def test_future_flags_and_capture_assignments_work_across_cells(tmp_path: Path) -> None:
    pytest.importorskip("IPython")
    result, _ = child(
        tmp_path,
        "# %%\nfrom __future__ import annotations\n"
        "# %%\ndef identity(value: NotImported) -> NotImported:\n    return value\n"
        "output = !echo ds60-local-fixture\nassert output == ['ds60-local-fixture']\n"
        "print(identity.__annotations__['value'])\n",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "NotImported" in result.stdout


def test_cell_magic_failure_reports_its_real_source_header(tmp_path: Path) -> None:
    pytest.importorskip("IPython")
    result, runtime = child(tmp_path, "# %%\nanswer = 1\n# %%\n\n%%not_a_real_magic\nbody\n")

    assert result.returncode != 0
    assert json.loads((runtime / "execution.json").read_text()) == {"error_line": 5}


@pytest.mark.skipif(os.name == "nt", reason="Creating a test symlink needs Windows developer mode.")
def test_error_metadata_replaces_a_symlink_without_changing_its_target(tmp_path: Path) -> None:
    sentinel = tmp_path / "existing-notes.txt"
    sentinel.write_text("preserved", encoding="utf-8")
    runtime = tmp_path / "private-runtime"
    runtime.mkdir()
    (runtime / "execution.json").symlink_to(sentinel)
    result, _ = child(tmp_path, "raise ValueError('record line only')\n")

    assert result.returncode != 0
    assert sentinel.read_text() == "preserved"
    assert not (runtime / "execution.json").is_symlink()
    assert json.loads((runtime / "execution.json").read_text()) == {"error_line": 1}


def test_inline_matplotlib_uses_headless_shell_support(tmp_path: Path) -> None:
    pytest.importorskip("IPython")
    if importlib.util.find_spec("matplotlib_inline") is None:
        pytest.skip("The selected test profile lacks optional inline plotting.")
    # This test exercises headless inline-shell semantics, not discovery of
    # every system font. Prepare the actual isolated cache in its own bounded
    # setup phase; the notebook child still retains its 25-second deadline.
    cache = tmp_path / "matplotlib-cache"
    prepared = subprocess.run(
        [sys.executable, "-c", "import matplotlib.font_manager"],
        cwd=tmp_path,
        env={
            **os.environ,
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(cache),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    cache_files = {path.name: path.read_bytes() for path in cache.glob("fontlist-v*.json")}
    assert cache_files, "Matplotlib setup did not write its isolated font cache."
    result, _ = child(
        tmp_path,
        "# %%\n%matplotlib inline\nimport matplotlib.pyplot as plt\n"
        "plt.plot([1, 2], [2, 3])\nprint('inline succeeded')\n",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "inline succeeded" in result.stdout
    assert {path.name: path.read_bytes() for path in cache.glob("fontlist-v*.json")} == cache_files


def test_interactive_gui_event_loops_fail_with_a_clear_boundary(tmp_path: Path) -> None:
    pytest.importorskip("IPython")
    result, runtime = child(tmp_path, "# %%\n%gui tk\n")

    assert result.returncode != 0
    assert "Interactive GUI event loops are unavailable" in result.stdout
    assert json.loads((runtime / "execution.json").read_text()) == {"error_line": 2}


@pytest.mark.parametrize("interactive", [False, True])
def test_argparse_receives_only_the_submitted_source_path(
    tmp_path: Path, interactive: bool
) -> None:
    if interactive:
        pytest.importorskip("IPython")
    source = (
        ("# %%\n" if interactive else "") + "import argparse, json, sys\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--with-processes', action='store_true')\n"
        "arguments = parser.parse_args()\n"
        "assert sys.argv == [__file__]\n"
        "print(json.dumps({'arguments': sys.argv[1:], 'processes': arguments.with_processes}))\n"
    )
    result, _ = child(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.strip()) == {"arguments": [], "processes": False}


@pytest.mark.parametrize("interactive", [False, True])
@pytest.mark.parametrize("outcome", ["success", "error", "exit-zero", "exit-seven"])
def test_caller_argv_object_and_values_are_restored_on_every_execution_outcome(
    tmp_path: Path, interactive: bool, outcome: str
) -> None:
    if interactive:
        pytest.importorskip("IPython")
    endings = {
        "success": "print('source completed')\n",
        "error": "raise ValueError('expected learner failure')\n",
        "exit-zero": "raise SystemExit(0)\n",
        "exit-seven": "raise SystemExit(7)\n",
    }
    source = (
        ("# %%\n" if interactive else "") + "import sys\nassert sys.argv == [__file__]\n"
        "sys.argv.append('learner-only')\nsys.argv = ['learner rebound argv']\n" + endings[outcome]
    )
    program = tmp_path / "submitted.py"
    program.write_text(source, encoding="utf-8")
    runtime = tmp_path / "private-runtime"
    # Keep the source path outside argv so the caller list contains only its
    # actual private worker options, and retain an alias to test object identity.
    driver = (
        "import json, sys\nfrom pathlib import Path\n"
        "from ds60sqlpy.notebook_execution import execute_python_file\n"
        "caller = ['worker', '--snapshot', 'private/source.py', '--figures', 'private/figures']\n"
        "expected = caller[:]\nsys.argv = caller\n"
        "result = None\nerror = None\n"
        "try:\n"
        f"    result = execute_python_file(Path({str(program)!r}), Path({str(runtime)!r}))\n"
        "except BaseException as exc:\n"
        "    error = type(exc).__name__\n"
        "    result = exc.code if isinstance(exc, SystemExit) else 1\n"
        "assert sys.argv is caller\nassert caller == expected\n"
        "print('CALLER_RESTORED:' + json.dumps({'result': result, 'error': error}))\n"
    )
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-c", driver],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=25,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    record = json.loads(result.stdout.rsplit("CALLER_RESTORED:", 1)[1].strip())
    expected_status = {"success": 0, "error": 1, "exit-zero": 0, "exit-seven": 7}[outcome]
    assert record["result"] == expected_status
    assert record["error"] == (
        None
        if interactive or outcome == "success"
        else "ValueError"
        if outcome == "error"
        else "SystemExit"
    )


@pytest.mark.parametrize("interactive", [False, True])
def test_real_pad_runner_does_not_forward_private_worker_arguments(
    tmp_path: Path, interactive: bool
) -> None:
    if interactive:
        pytest.importorskip("IPython")
    from dataclasses import replace

    from ds60sqlpy.catalog import Catalog
    from ds60sqlpy.execution import PadRunner

    lesson = replace(Catalog.load().get("python-01"), prerequisites=())
    runner = PadRunner(Catalog(tmp_path, (lesson,)), python=sys.executable)
    source = (
        ("# %%\n" if interactive else "") + "import argparse, json, sys\n"
        "arguments = argparse.ArgumentParser().parse_args()\n"
        "assert sys.argv == [__file__]\n"
        "print('PAD_ARGUMENTS:' + json.dumps(sys.argv[1:]))\n"
    )
    result = runner.run("python-01", "python", source)
    assert result["returncode"] == 0, result["output"]
    assert "PAD_ARGUMENTS:[]" in result["output"]
