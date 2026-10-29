"""Scala companion preparation guards and source-bound native qualification."""

from __future__ import annotations

import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "courses/advanced-spark-modeling/projects/spark-tmb"
SCALA = PROJECT / "scala"


def runner() -> dict[str, Any]:
    return runpy.run_path(str(SCALA / "run.py"))


def test_compiler_entrypoint_help_needs_no_runtime_or_download() -> None:
    result = subprocess.run(
        [sys.executable, str(SCALA / "run.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0 and "--compile-only" in result.stdout
    assert "prepared Spark jars" in result.stdout


def test_compiler_rejects_missing_exact_spark_before_starting_any_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    namespace = runner()
    monkeypatch.setenv("SPARK_HOME", str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["run.py", "--compile-only"])

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No toolchain/download should start without the declared Spark jars")

    monkeypatch.setattr(subprocess, "run", forbidden)
    with pytest.raises(SystemExit, match="exact Spark 4.0.1"):
        namespace["main"]()


def test_compiler_rejects_wrong_jdk_before_compilation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    namespace = runner()
    jars = tmp_path / "jars"
    jars.mkdir()
    (jars / "spark-sql_2.13-4.0.1.jar").write_bytes(b"guard fixture, never loaded")
    monkeypatch.setenv("SPARK_HOME", str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["run.py", "--compile-only"])
    calls: list[list[str]] = []

    def wrong_version(arguments: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(arguments)
        return subprocess.CompletedProcess(
            arguments, 0, stdout="", stderr='openjdk version "17.0.1"'
        )

    monkeypatch.setattr(subprocess, "run", wrong_version)
    with pytest.raises(SystemExit, match="JDK 21"):
        namespace["main"]()
    assert calls == [["java", "-version"]]


def test_scala_reuses_parent_registered_models_and_documented_protocol() -> None:
    registry = json.loads((PROJECT / "registry.json").read_text())
    assert registry["models"]["normal_mean"]["factorization"] == "independent_rows"
    assert registry["models"]["normal_mean"]["fixed_parameters"] == ["mu", "log_sigma"]
    assert registry["models"]["random_intercept"]["factorization"] == "complete_groups"
    assert (PROJECT / "spark_tmb/cli.py").is_file()
    assert (PROJECT / "CLI-CONTRACT.md").is_file()
    assert not (SCALA / "registry.json").exists()
    assert not list(SCALA.rglob("*.cpp"))
    assert not list(SCALA.rglob("*.so"))
    assert not list(SCALA.rglob("*.jar"))


def test_native_scala_receipt_binds_complete_sources_and_numerical_oracles() -> None:
    receipt = json.loads((SCALA / "qualification.json").read_text())
    assert receipt["platform"] == "linux/arm64"
    assert receipt["returncode"] == 0
    assert receipt["compilation"]["compiled"] is True
    assert receipt["compilation"]["executed"] is True
    evidence = receipt["result"]
    assert evidence["passed"] is True
    assert evidence["spark"] == "4.0.1"
    assert evidence["java"].startswith("21.")
    assert evidence["raw_observations_collected"] is False
    assert evidence["caller_cache_preserved"] is True
    assert evidence["empty_partitions_checked"] is True
    assert evidence["remote_cluster"] is False and evidence["gpu"] is False
    assert len(evidence["partition_batch_cases"]) == 3
    assert all(
        case["rows"] == 12 and case["oracle_error"] < 1e-10
        for case in evidence["partition_batch_cases"]
    )
    assert evidence["fit"]["converged"] is True
    assert evidence["fit"]["mu"] == pytest.approx(2.0, abs=1e-6)
    assert evidence["fit"]["gradient_inf_norm"] < 1e-6
    assert "duplicate observation identity" in evidence["rejected_cases"]
    assert "complete groups cannot be row-batched" in evidence["rejected_cases"]
    for relative, digest in receipt["owned_source_sha256"].items():
        assert hashlib.sha256((SCALA / relative).read_bytes()).hexdigest() == digest
