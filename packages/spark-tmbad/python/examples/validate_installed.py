"""Actual installed-wheel / Spark / native acceptance, never a mocked Spark test.

Run with spark-submit --jars PREPARED.jar validate_installed.py --manifest FILE.
The driver fixture DataFrames use Spark SQL, without Python executor functions.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import tempfile
from pathlib import Path

import ds60_spark_tmbad
from ds60_spark_tmbad import ContractError, FittedModel, ModelSpec, PreparedRuntime, SparkTMBad
from pyspark.sql import SparkSession


def close(actual, expected, *, tolerance=2e-4):
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"Expected {expected!r}; received {actual!r}")


def converged(fitted):
    if not fitted.model["fit"]["converged"]:
        raise AssertionError(f"Fit did not converge: {fitted.model['fit']}")


def check_installed():
    dist = importlib.metadata.distribution("ds60-spark-tmbad")
    expected = Path(dist.locate_file("ds60_spark_tmbad/__init__.py")).resolve()
    actual = Path(ds60_spark_tmbad.__file__).resolve()
    if actual != expected or dist.version != ds60_spark_tmbad.__version__:
        raise AssertionError("The imported package must be the non-editable installed wheel")


def check_normal(api, spark):
    observations = spark.sql(
        "SELECT id AS row_id, CAST(id + 1 AS DOUBLE) AS y FROM range(4)"
    ).repartition(3)
    spec = ModelSpec("normal", {"y": "y"}, id_columns=["row_id"])
    fitted = api.fit_shared(observations, spec, options={"initial_parameters": [2.0, 0.0]})
    converged(fitted)
    close(fitted.model["parameters"][0], 2.5)
    close(math.exp(fitted.model["parameters"][1]), math.sqrt(1.25))
    requested = spark.sql("SELECT id + 100 AS row_id FROM range(3)")
    predictions = (
        fitted.predict(requested, options={"target": "response", "columns": {}})
        .orderBy("row_id")
        .collect()
    )
    assert [row.row_id for row in predictions] == [100, 101, 102]
    for row in predictions:
        close(row.tmbad_mean, 2.5)
        close(row.tmbad_sd, math.sqrt(1.25))
    with tempfile.TemporaryDirectory(prefix="spark-tmbad-model-") as directory:
        path = Path(directory) / "normal.json"
        fitted.save(path)
        loaded = FittedModel.load(path, runtime=api.runtime)
        assert loaded.to_json() == fitted.to_json()
        assert loaded.predict(requested, options={"target": "response", "columns": {}}).count() == 3
        wrong = api.runtime.manifest
        wrong["binary"]["sha256"] = "0" * 64
        try:
            FittedModel.load(path, runtime=PreparedRuntime(wrong))
        except ContractError:
            pass
        else:
            raise AssertionError("Model loading accepted a changed native binary identity")
    return "normal shared fit, response-free prediction and source-bound JSON round trip"


def check_groups(api, spark):
    observations = spark.sql("""
        SELECT id AS row_id,
               CASE WHEN id < 4 THEN 'A' ELSE 'B' END AS series,
               CAST(id % 4 + 1 + CASE WHEN id < 4 THEN 0 ELSE 10 END AS DOUBLE) AS y
        FROM range(8)
    """).repartition(3)
    fitted = api.fit_groups(
        observations,
        ModelSpec("normal", {"y": "y"}, id_columns=["row_id"], group_columns=["series"]),
        options={"initial_parameters": [7.0, 2.0], "max_iterations": 200},
    )
    requested = spark.sql("SELECT 100 AS row_id, 'A' AS series UNION ALL SELECT 101, 'B'")
    with tempfile.TemporaryDirectory(prefix="spark-tmbad-groups-") as directory:
        # This local storage check is for local Spark only. Cluster callers need
        # explicitly shared storage supported by their Spark deployment.
        path = str(Path(directory) / "models")
        fitted.models.write.mode("errorifexists").parquet(path)
        restored = api.from_group_models(spark.read.parquet(path))
        predicted = (
            restored.predict(requested, options={"target": "response", "columns": {}})
            .orderBy("row_id")
            .collect()
        )
        close(predicted[0].tmbad_mean, 2.5)
        close(predicted[1].tmbad_mean, 12.5)
        for row in predicted:
            close(row.tmbad_sd, math.sqrt(1.25))
        repeated = (
            restored.predict(requested, options={"target": "response", "columns": {}})
            .orderBy("row_id")
            .collect()
        )
        assert repeated == predicted
        forecast = (
            restored.forecast(
                observations.limit(0),
                requested,
                options={"target": "response", "history_columns": {"y": "y"}, "future_columns": {}},
            )
            .orderBy("row_id")
            .collect()
        )
        assert forecast == predicted
    return "independent group fits, JVM model join, predictions and persisted model rows"


def check_random_intercept(api, spark):
    observations = spark.sql("""
        SELECT id AS row_id, CAST(FLOOR(id / 4) AS STRING) AS series,
               CAST(FLOOR(id / 4) + 1 +
                    CASE id % 4 WHEN 0 THEN -0.4 WHEN 1 THEN 0.4
                                WHEN 2 THEN -0.2 ELSE 0.2 END AS DOUBLE) AS y
        FROM range(20)
    """).repartition(3)
    spec = ModelSpec(
        "gaussian_random_intercept",
        {"y": "y"},
        id_columns=["row_id"],
        group_columns=["series"],
    )
    fitted = api.fit_shared(
        observations,
        spec,
        options={"initial_parameters": [2.9, math.log(0.4), math.log(1.4)], "max_iterations": 150},
    )
    converged(fitted)
    beta, log_sigma, log_tau = fitted.model["parameters"]
    sigma2, tau2 = math.exp(2 * log_sigma), math.exp(2 * log_tau)
    close(beta, 3.0)
    close(sigma2, 2.0 / 15.0, tolerance=1e-3)
    close(tau2, 2.0 - sigma2 / 4, tolerance=1e-3)
    history = observations.where("series = '0'")
    future = spark.sql("SELECT id + 100 AS row_id, '0' AS series FROM range(2)")
    expected_mean = beta + (4 * tau2 / (sigma2 + 4 * tau2)) * (1.0 - beta)
    expected_variance = sigma2 + tau2 * sigma2 / (sigma2 + 4 * tau2)
    predicted = fitted.predict(
        future,
        history=history,
        options={"target": "existing_group", "columns": {}, "history_columns": {"y": "y"}},
    ).collect()
    forecast = fitted.forecast(
        history,
        future,
        options={"target": "existing_group", "history_columns": {"y": "y"}, "future_columns": {}},
    ).collect()
    for row in predicted + forecast:
        close(row.tmbad_mean, expected_mean)
        close(row.tmbad_variance, expected_variance)
    new_group = spark.sql("SELECT 200 AS row_id, 'unseen' AS series")
    row = fitted.predict(new_group, options={"target": "new_group", "columns": {}}).first()
    close(row.tmbad_mean, beta)
    close(row.tmbad_variance, sigma2 + tau2)
    return "exact random-intercept fit, existing/new group prediction and conditional forecast"


def check_ar1(api, spark):
    innovations = [-0.3, 0.2, 0.5, -0.4, 0.1, -0.6, 0.4, 0.3, -0.2, 0.6, -0.1, -0.5] * 3
    values, previous = [], 1.2
    for index, innovation in enumerate(innovations):
        previous = 1.0 + 0.6 * (previous - 1.0) + innovation
        values.append(f"({index}, {index}, 'A', CAST({previous!r} AS DOUBLE))")
    history = spark.sql(
        "SELECT * FROM VALUES " + ",".join(values) + " AS observations(row_id, time, series, y)"
    ).repartition(3)
    spec = ModelSpec(
        "ar1",
        {"time": "time", "y": "y"},
        id_columns=["row_id"],
        group_columns=["series"],
        order_columns=["time"],
    )
    fitted = api.fit_shared(
        history,
        spec,
        options={
            "initial_parameters": [1.0, math.atanh(0.4), math.log(0.5)],
            "max_iterations": 200,
        },
    )
    converged(fitted)
    mu, unconstrained_phi, log_sigma = fitted.model["parameters"]
    phi, sigma2 = math.tanh(unconstrained_phi), math.exp(2 * log_sigma)
    future = spark.sql(
        f"SELECT id + 1000 AS row_id, id + {len(values)} AS time, 'A' AS series FROM range(3)"
    )
    forecast = (
        fitted.forecast(
            history,
            future,
            options={
                "target": "conditional_history",
                "history_columns": {"time": "time", "y": "y"},
                "future_columns": {"time": "time"},
            },
        )
        .orderBy("row_id")
        .collect()
    )
    for horizon, row in enumerate(forecast, 1):
        close(row.tmbad_mean, mu + phi**horizon * (previous - mu))
        close(row.tmbad_variance, sigma2 * sum(phi ** (2 * j) for j in range(horizon)))
    requested = spark.sql(
        f"SELECT 2000 AS row_id, 'A' AS series, CAST({previous!r} AS DOUBLE) AS lag"
    )
    one_step = fitted.predict(
        requested, options={"target": "response", "columns": {"lag": "lag"}}
    ).first()
    close(one_step.tmbad_mean, forecast[0].tmbad_mean)
    close(one_step.tmbad_variance, forecast[0].tmbad_variance)
    return "ordered AR1 fit, response-free lag prediction and three-step conditional forecast"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument(
        "--case", choices=["all", "normal", "groups", "random-intercept", "ar1"], default="all"
    )
    args = parser.parse_args()
    check_installed()
    runtime = PreparedRuntime.from_manifest(args.manifest)
    spark = SparkSession.builder.appName("spark-tmbad-installed-acceptance").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    try:
        api = SparkTMBad(runtime)
        assert api.describe(spark, "normal")["parameter_names"] == ["mu", "log_sigma"]
        api.probe(spark, "normal")
        checks = {
            "normal": check_normal,
            "groups": check_groups,
            "random-intercept": check_random_intercept,
            "ar1": check_ar1,
        }
        results = [
            check(api, spark) for name, check in checks.items() if args.case in ("all", name)
        ]
        print(
            json.dumps(
                {
                    "status": "passed",
                    "scope": "actual local Spark and native execution",
                    "python_package": ds60_spark_tmbad.__version__,
                    "spark_version": spark.version,
                    "artifact_build_id": runtime.manifest["build_id"],
                    "platform": runtime.manifest["platform"],
                    "checks": results,
                },
                sort_keys=True,
            )
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
