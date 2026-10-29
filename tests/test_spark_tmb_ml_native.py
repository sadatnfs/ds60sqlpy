"""Run the shipped real ML acceptance cases inside a prepared native environment."""

from __future__ import annotations

import importlib
import os
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

if os.environ.get("DS60_SPARK_TMB_NATIVE") != "1":
    pytest.skip("Prepared Spark/TMB environment is required", allow_module_level=True)
pytest.importorskip("pyspark")
PROJECT = Path(__file__).resolve().parents[1] / "courses/advanced-spark-modeling/projects/spark-tmb"
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
native_checks = importlib.import_module("check_dataframe_ml")
check_groups = native_checks.check_groups
check_normal = native_checks.check_normal
check_regression = native_checks.check_regression
SparkSession = importlib.import_module("pyspark.sql").SparkSession


@pytest.fixture(scope="module")
def spark() -> Iterator[Any]:
    session = (
        SparkSession.builder.master("local[2]")
        .appName("tmb-ml-native-tests")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.task.maxFailures", "1")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


def test_actual_normal_dataframe_ml_roundtrip(spark: Any, tmp_path: Path) -> None:
    assert check_normal(spark, tmp_path)["predicted_rows"] == 2


def test_actual_vector_regression_pipeline_roundtrip(spark: Any, tmp_path: Path) -> None:
    assert len(check_regression(spark, tmp_path)["parameters"]) == 3


def test_actual_complete_group_contracts(spark: Any) -> None:
    assert check_groups(spark)["rows"] == 4
