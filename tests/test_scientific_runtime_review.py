"""Independent output-fidelity and successful-computation failure boundaries."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from ds60sqlpy import dbt_runner, plot_artifacts, stan_runner
from ds60sqlpy.execution import PYTHON_WORKER

ROOT = Path(__file__).resolve().parents[1]


def _changing_directory_program() -> str:
    return (
        "from pathlib import Path\n"
        "import os\n"
        "from ds60sqlpy.plot_artifacts import publish_report\n"
        "Path('project').mkdir()\n"
        "os.chdir('project')\n"
        "publish_report({'answer': 42}, description='Completed nested project')\n"
        "print('Computation succeeded')\n"
    )


def _environment() -> dict[str, str]:
    return dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONDONTWRITEBYTECODE="1")


def test_modern_publisher_keeps_job_identity_after_working_directory_change(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text(_changing_directory_program())
    run = subprocess.run(
        [sys.executable, "-m", "ds60sqlpy.worker_figures"],
        cwd=tmp_path,
        env=_environment(),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert run.returncode == 0, run.stderr
    artifacts, warning = plot_artifacts.read_artifacts(tmp_path)
    assert warning == ""
    assert artifacts == [
        {"kind": "json", "description": "Completed nested project", "data": {"answer": 42}}
    ]
    assert not (tmp_path / "project/ds60-figures.json").exists()


def test_legacy_publisher_retains_separate_runtime_destination(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    source.write_text(_changing_directory_program())
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    run = subprocess.run(
        [sys.executable, "-c", PYTHON_WORKER, str(source), str(runtime)],
        cwd=tmp_path,
        env=_environment(),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert run.returncode == 0, run.stderr
    artifacts, warning = plot_artifacts.read_artifacts(runtime)
    assert not warning and artifacts[0]["data"] == {"answer": 42}


def _chart_table(value: Any) -> dict[str, Any]:
    return {
        "kind": "plotly",
        "figure": {
            "data": [{"type": "scatter", "x": [0], "y": [1]}],
            "layout": {"meta": {"table": {"columns": ["record_id"], "rows": [[value]]}}},
        },
    }


@pytest.mark.parametrize("value", [9_007_199_254_740_993, -9_007_199_254_740_993])
def test_accessible_chart_tables_reject_integers_a_browser_would_change(value: int) -> None:
    with pytest.raises(ValueError, match="integer|precision|string"):
        plot_artifacts.validate_artifacts([_chart_table(value)])
    exact = plot_artifacts.validate_artifacts([_chart_table(str(value))])
    assert exact[0]["table"]["rows"] == [[str(value)]]
    safe = plot_artifacts.validate_artifacts([_chart_table(9_007_199_254_740_991)])
    assert safe[0]["table"]["rows"] == [[9_007_199_254_740_991]]


def test_failed_atomic_append_preserves_prior_saved_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(plot_artifacts, "_OUTPUT_DIRECTORY", tmp_path)
    plot_artifacts.publish_report({"original": "retained"}, description="First result")
    path = tmp_path / "ds60-figures.json"
    before = path.read_bytes()

    def unavailable_replace(self: Path, target: str | Path) -> Path:
        assert Path(target) == path
        raise OSError("simulated storage failure")

    monkeypatch.setattr(Path, "replace", unavailable_replace)
    with pytest.raises(OSError, match="simulated storage"):
        plot_artifacts.publish_table(["value"], [[42]], description="Second result")
    assert path.read_bytes() == before
    assert not list(tmp_path.glob(".ds60-output-*"))
    assert json.loads(path.read_text())[0]["data"] == {"original": "retained"}


def test_stan_output_storage_failure_does_not_change_completed_sampling_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(plot_artifacts, "_OUTPUT_DIRECTORY", None)
    calls: list[list[str]] = []

    def successful_run(
        command: list[str], *, check: bool = False
    ) -> subprocess.CompletedProcess[bytes]:
        assert check is False
        calls.append(command)
        if "stansummary" in command[0]:
            (tmp_path / "summary.csv").write_text("name,Mean,StdDev\nmu,1.9,0.4\n")
        return subprocess.CompletedProcess(command, 0)

    def finite_draws(path: Path) -> list[dict[str, float]]:
        assert path.name in {"chain-1.csv", "chain-2.csv"}
        return [{"mu": 1.9 + number * 0.001, "divergent__": 0.0} for number in range(100)]

    def unavailable_output(*args: Any, **kwargs: Any) -> None:
        raise OSError("simulated artifact storage failure")

    monkeypatch.setattr(subprocess, "run", successful_run)
    monkeypatch.setattr(stan_runner, "read_draws", finite_draws)
    monkeypatch.setattr(plot_artifacts, "publish_table", unavailable_output)
    monkeypatch.setattr(plot_artifacts, "publish_artifact", unavailable_output)
    assert stan_runner.main() == 0
    assert len(calls) == 3
    captured = capsys.readouterr()
    assert "simulated artifact storage failure" in captured.err + captured.out
    assert "sampling completed" in captured.out.casefold()


def test_mixed_structured_and_chart_outputs_keep_order_and_the_two_output_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(plot_artifacts, "_OUTPUT_DIRECTORY", tmp_path)
    plot_artifacts.publish_report({"training_rows": 42}, description="Model provenance")
    plot_artifacts.publish_artifact(_chart_table(42))
    target = tmp_path / "ds60-figures.json"
    before = target.read_bytes()
    with pytest.raises(ValueError, match="two"):
        plot_artifacts.publish_table(["extra"], [[1]], description="Third result")
    assert target.read_bytes() == before
    records, warning = plot_artifacts.read_artifacts(tmp_path)
    assert not warning and [row["kind"] for row in records] == ["json", "plotly"]
    assert records[0]["data"] == {"training_rows": 42}
    assert records[1]["table"]["rows"] == [[42]]


def test_dbt_publication_failure_preserves_a_successful_materialization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(plot_artifacts, "_OUTPUT_DIRECTORY", None)
    (tmp_path / "model.sql").write_text("select 42 as answer")
    commands: list[str] = []
    queries: list[str] = []

    def prepare(directory: Path, source: str) -> Path:
        assert directory == tmp_path and source == "select 42 as answer"
        project = directory / "project"
        (project / "target").mkdir(parents=True)
        node = {
            "schema": "main",
            "alias": 'quoted"model',
            "unique_id": "model.classroom.lesson_model",
            "config": {"materialized": "table"},
            "depends_on": {"nodes": []},
            "compiled_code": source,
        }
        (project / "target/manifest.json").write_text(
            json.dumps({"nodes": {node["unique_id"]: node}})
        )
        return project

    class Runner:
        def invoke(self, arguments: list[str]) -> SimpleNamespace:
            command = next(value for value in arguments if value in {"seed", "build"})
            commands.append(command)
            return SimpleNamespace(success=True, exception=None)

    class Connection:
        description = [("answer", "INTEGER")]

        def __enter__(self) -> Connection:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def execute(self, query: str) -> Connection:
            queries.append(query)
            return self

        def fetchone(self) -> tuple[int]:
            return (1,)

        def fetchall(self) -> list[tuple[int]]:
            return [(42,)]

    def connect(*args: Any, **kwargs: Any) -> Connection:
        return Connection()

    original_import = importlib.import_module

    def prepared_module(name: str, package: str | None = None) -> Any:
        if name == "duckdb":
            return SimpleNamespace(connect=connect)
        if name == "dbt.cli.main":
            return SimpleNamespace(dbtRunner=Runner)
        return original_import(name, package)

    def unavailable_output(*args: Any, **kwargs: Any) -> None:
        raise OSError("simulated dbt result storage failure")

    monkeypatch.setattr(dbt_runner, "prepare", prepare)
    monkeypatch.setattr(importlib, "import_module", prepared_module)
    monkeypatch.setattr(dbt_runner, "publish_table", unavailable_output)
    monkeypatch.setattr(dbt_runner, "publish_report", unavailable_output)
    assert dbt_runner.main() == 0
    assert commands == ["seed", "build"]
    assert all('"quoted""model"' in query for query in queries)
    captured = capsys.readouterr()
    assert "simulated dbt result storage failure" in captured.err + captured.out
    assert "built successfully" in captured.out


@pytest.mark.parametrize("failed_command", ["seed", "build"])
def test_dbt_execution_failure_survives_a_second_failure_saving_its_report(
    failed_command: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(plot_artifacts, "_OUTPUT_DIRECTORY", None)
    (tmp_path / "model.sql").write_text("select missing_column from missing_table")
    project = tmp_path / "project"
    (project / "target").mkdir(parents=True)
    calls: list[str] = []
    reports: list[dict[str, Any]] = []

    def prepare(directory: Path, source: str) -> Path:
        assert directory == tmp_path and "missing_column" in source
        return project

    class Runner:
        def invoke(self, arguments: list[str]) -> SimpleNamespace:
            command = next(value for value in arguments if value in {"seed", "build"})
            calls.append(command)
            if command == failed_command:
                (project / "target/run_results.json").write_text(
                    json.dumps(
                        {
                            "results": [
                                {
                                    "unique_id": "model.classroom.lesson_model",
                                    "status": "error",
                                    "message": "Database rejected missing_table",
                                }
                            ]
                        }
                    )
                )
            return SimpleNamespace(success=command != failed_command, exception=None)

    original_import = importlib.import_module

    def prepared_module(name: str, package: str | None = None) -> Any:
        if name == "dbt.cli.main":
            return SimpleNamespace(dbtRunner=Runner)
        if name == "duckdb":
            return SimpleNamespace()
        return original_import(name, package)

    def unavailable_report(data: dict[str, Any], *, description: str) -> None:
        assert "execution failed" in description
        reports.append(data)
        raise OSError("error report storage unavailable")

    monkeypatch.setattr(dbt_runner, "prepare", prepare)
    monkeypatch.setattr(importlib, "import_module", prepared_module)
    monkeypatch.setattr(dbt_runner, "publish_report", unavailable_report)
    assert dbt_runner.main() == 1
    assert calls == (["seed"] if failed_command == "seed" else ["seed", "build"])
    assert len(reports) == 1
    assert reports[0]["commands"][-1] == {"command": failed_command, "success": False}
    assert reports[0]["node_failures"][0]["message"] == "Database rejected missing_table"
    captured = capsys.readouterr()
    assert "error report storage unavailable" in captured.err
    assert "built successfully" not in captured.out
