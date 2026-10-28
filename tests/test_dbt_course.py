"""Teaching, artifact and independent state contracts for the real dbt path."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/dbt"


def reference(number: int) -> ModuleType:
    pytest.importorskip("dbt.cli.main", reason="Prepared dbt runtime required")
    pytest.importorskip("duckdb", reason="Prepared dbt runtime required")
    spec = importlib.util.spec_from_file_location(
        f"dbt_course_{number}", BASE / "references" / f"dbt-{number:03}_reference.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dbt_complete_subject_contract() -> None:
    track = json.loads((BASE / "track.json").read_text())
    admission = json.loads((BASE / "lessons.json").read_text())
    assert track["id"] == admission["track_id"] == "dbt"
    assert [row["id"] for row in track["lessons"]] == [f"dbt-{n:03}" for n in range(1, 27)]
    assert {row["level"] for row in track["lessons"]} == {"beginner", "intermediate", "advanced"}
    variants = {}
    for row in admission["lessons"]:
        assert row["verification_id"] is None
        assert row["runtime_profile"] == "data-engineering"
        for path in (row["guide_path"], row["source_path"], *row["solution_paths"]):
            assert (ROOT / path).is_file()
        guide = (ROOT / row["guide_path"]).read_text()
        assert guide.count("## Worked case ") == 2
        assert all(f"### {n}. " in guide for n in range(1, 7))
        assert len(re.sub(r"```.*?```", "", guide, flags=re.S).split()) >= 600
        assert "—" not in guide
        for variant in row.get("variants", []):
            assert variant["id"] == "sql-model"
            assert variant["runtime_profile"] == "dbt-duckdb"
            assert variant["language"] == "sql"
            assert variant["verification_id"] is None
            for path in (variant["source_path"], *variant["solution_paths"]):
                assert (ROOT / path).is_file()
            variants[row["id"]] = variant
    assert set(variants) == {"dbt-001", "dbt-002", "dbt-003", "dbt-007"}


def test_dbt_authoring_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(BASE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_dbt_actual_unit_tests_are_independent_of_seed() -> None:
    module = reference(6)
    correct, broken = module.example_one(), module.example_two()
    assert correct["status"] == "pass"
    assert broken["status"] == "fail"
    assert correct["production_seed_unchanged"] == broken["production_seed_unchanged"] == 100


def test_dbt_defer_preserves_production_parent() -> None:
    result = reference(20).example_one()
    assert result == {"deferred_parent": "prod.base", "child": 11, "dev_parent_not_built": True}


def test_dbt_temporal_availability_has_an_independent_oracle() -> None:
    module = reference(17)
    valid, leaked = module.example_one(), module.example_two()
    events = [(2, 3, 10), (4, 7, 999), (8, 8, 30)]
    expected = [
        (i, max((r for r in events if r[0] <= t and r[1] <= t), key=lambda r: r[:2])[2])
        for i, t in [(1, 5), (2, 9)]
    ]
    assert valid["features"] == expected == [(1, 10), (2, 30)]
    assert leaked["features"] != expected


def test_dbt_failed_candidate_preserves_accepted_release() -> None:
    module = reference(25)
    assert module.example_one()["retained_release"] == [1, 42]
    result = module.example_two()
    assert result == {"candidate_rejected": 99, "accepted_release_unchanged": 42}


def test_dbt_complete_retail_project(tmp_path: Path) -> None:
    pytest.importorskip("dbt.cli.main", reason="Prepared dbt runtime required")
    duckdb = pytest.importorskip("duckdb", reason="Prepared dbt runtime required")
    project = tmp_path / "retail"
    shutil.copytree(BASE / "projects/retail", project)
    env = dict(os.environ, DBT_SEND_ANONYMOUS_USAGE_STATS="false", DO_NOT_TRACK="true")

    def run(*arguments: str, success: bool = True) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "dbt.cli.main",
                "--no-send-anonymous-usage-stats",
                *arguments,
                "--profiles-dir",
                str(project),
            ],
            cwd=project,
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert (result.returncode == 0) is success, result.stdout + result.stderr

    run("deps")
    run("build")
    run_results = json.loads((project / "target/run_results.json").read_text())
    by_type = {row["unique_id"].split(".")[0] for row in run_results["results"]}
    assert {"seed", "model", "test", "unit_test", "snapshot"} <= by_type
    assert all(
        row["status"] in {"success", "pass"}
        or (row["unique_id"].startswith("exposure.") and row["status"] == "no-op")
        for row in run_results["results"]
    )
    with duckdb.connect(str(project / "target/warehouse.duckdb")) as connection:
        rows = connection.execute(
            "select customer_id, net_amount from dev.customer_revenue order by customer_id"
        ).fetchall()
    assert [(key, float(value)) for key, value in rows] == [(10, 75.0), (20, 170.0), (30, 0.0)]
    assert sum(float(value) for _, value in rows) == 100 + 50 - 25 + 0 + 120
    run("docs", "generate")
    manifest = json.loads((project / "target/manifest.json").read_text())
    catalog = json.loads((project / "target/catalog.json").read_text())
    assert "model.learning_retail.customer_revenue" in catalog["nodes"]
    assert "exposure.learning_retail.customer_review" in manifest["exposures"]
    assert "macro.quality_utils.recognized_amount" in manifest["macros"]
    customers = project / "seeds/customers.csv"
    customers.write_text(customers.read_text() + "10,Duplicate,north\n")
    run("build", success=False)
    failures = json.loads((project / "target/run_results.json").read_text())["results"]
    assert any(row["status"] == "fail" and "unique" in row["unique_id"] for row in failures)
