"""Real local[2] DataFrame/ML acceptance, with no pytest runtime dependency."""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from pyspark.ml import Pipeline, PipelineModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from spark_tmb import runtime
from spark_tmb.dataframe import DataFrameObjective, artifact_identity
from spark_tmb.fixed_bridge import laplace_oracle
from spark_tmb.ml import TMBEstimator, TMBModel
from spark_tmb.registry import ModelContractError


def expect_failure(call, message, exception=Exception):
    try:
        call()
    except exception as error:
        if message not in str(error):
            raise AssertionError(f"Unexpected failure instead of {message}: {error}") from error
    else:
        raise AssertionError(f"Expected failure containing {message}")


def check_normal(spark, directory):
    values = [-1.0, 0.0, 1.0, 2.0, 4.0, 5.0]
    training = (
        spark.createDataFrame(
            [(f"r{i}", y) for i, y in enumerate(values)], "row_id string, outcome double"
        )
        .repartition(2)
        .cache()
    )
    try:
        training.count()
        estimator = TMBEstimator(
            modelId="normal_location",
            dataCols={"y": "outcome"},
            initialParameters=[0.0, math.log(2.0)],
            parameterBounds=[[-10.0, 10.0], [-5.0, 5.0]],
            tol=1e-5,
            maxIter=80,
        )
        with patch.object(
            type(training), "collect", side_effect=AssertionError("Raw training rows collected")
        ):
            fitted = estimator.fit(training)
        assert training.is_cached
        mean = sum(values) / len(values)
        scale = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))
        np.testing.assert_allclose(fitted.parameters, [mean, math.log(scale)], atol=1e-4, rtol=0)
        future = spark.createDataFrame(
            [("z", "keep-z"), ("a", "keep-a")], "row_id string, label string"
        )
        predicted = fitted.transform(future)
        assert predicted.columns == ["row_id", "label", "prediction"]
        results = {row.row_id: (row.label, row.prediction) for row in predicted.collect()}
        assert (
            set(results) == {"a", "z"}
            and results["a"][0] == "keep-a"
            and results["z"][0] == "keep-z"
        )
        np.testing.assert_allclose(
            [results["a"][1], results["z"][1]], [mean, mean], atol=1e-4, rtol=0
        )
        model_path = directory / "normal-model"
        fitted.save(str(model_path))
        loaded = TMBModel.load(str(model_path))
        assert loaded.parameters == fitted.parameters
        assert loaded.transform(future).count() == 2
        estimator_path = directory / "estimator"
        estimator.save(str(estimator_path))
        restored = TMBEstimator.load(str(estimator_path))
        assert restored.getOrDefault(restored.dataCols) == {"y": "outcome"}
        fitted.write().overwrite().save(str(model_path))
        assert TMBModel.load(str(model_path)).parameters == fitted.parameters
        payload = json.loads((model_path / "model.json").read_text())
        payload["prepared"]["registry_sha256"] = "f" * 64
        (model_path / "model.json").write_text(json.dumps(payload))
        expect_failure(lambda: TMBModel.load(str(model_path)), "artifact", ModelContractError)
        return {
            "rows": len(values),
            "parameters": list(fitted.parameters),
            "score": fitted.fit_summary["projected_gradient_inf_norm"],
            "predicted_rows": len(results),
        }
    finally:
        training.unpersist()


def check_regression(spark, directory):
    x = np.arange(-2.0, 6.0)
    noise = np.array([0.2, -0.1, 0.1, -0.2, 0.1, -0.1, 0.15, -0.15])
    y = 1.5 + 0.8 * x + noise
    frame = spark.createDataFrame(
        [(int(i), float(a), float(b)) for i, (a, b) in enumerate(zip(x, y, strict=True))],
        "row_id int, feature double, response double",
    ).repartition(2)
    estimator = TMBEstimator(
        modelId="linear_regression",
        dataCols={"y": "response", "x": "feature"},
        initialParameters=[0.0, 0.0, 0.0],
        parameterBounds=[[-10.0, 10.0], [-10.0, 10.0], [-5.0, 3.0]],
        tol=1e-5,
        maxIter=100,
    )
    pipeline = Pipeline(stages=[estimator]).fit(frame)
    fitted = pipeline.stages[0]
    expected = np.linalg.lstsq(np.column_stack([np.ones(len(x)), x]), y, rcond=None)[0]
    np.testing.assert_allclose(fitted.parameters[:2], expected, atol=1e-4, rtol=0)
    expected_scale = math.sqrt(float(np.mean((y - expected[0] - expected[1] * x) ** 2)))
    np.testing.assert_allclose(fitted.parameters[2], math.log(expected_scale), atol=1e-4, rtol=0)
    future = spark.createDataFrame([(20, -3.0), (19, 6.0)], "row_id int, feature double")
    output = {row.row_id: row.prediction for row in pipeline.transform(future).collect()}
    np.testing.assert_allclose(
        [output[20], output[19]],
        [expected[0] - 3 * expected[1], expected[0] + 6 * expected[1]],
        atol=1e-4,
        rtol=0,
    )
    pipeline_path = directory / "pipeline"
    pipeline.save(str(pipeline_path))
    loaded = PipelineModel.load(str(pipeline_path))
    restored = {row.row_id: row.prediction for row in loaded.transform(future).collect()}
    assert set(restored) == set(output)
    np.testing.assert_allclose(
        [restored[20], restored[19]], [output[20], output[19]], atol=1e-12, rtol=0
    )
    expect_failure(
        lambda: fitted.transform(future.withColumnRenamed("feature", "absent")),
        "incompatible numeric type",
        ModelContractError,
    )
    expect_failure(
        lambda: fitted.transform(future.withColumn("prediction", future["feature"])),
        "new simple column",
        ModelContractError,
    )
    return {
        "parameters": list(fitted.parameters),
        "coefficient_oracle": expected.tolist(),
        "scale_oracle": expected_scale,
        "score": fitted.fit_summary["projected_gradient_inf_norm"],
    }


def check_groups(spark):
    records = [("b", 2, 2.4), ("a", 1, 0.1), ("b", 1, 2.0), ("a", 2, 0.3)]
    frame = (
        spark.createDataFrame(records, "unit string, ordinal int, y double")
        .withColumn("latent_group", lit(0))
        .repartition(2)
    )
    theta = [0.7, math.log(0.4), math.log(0.8)]
    with DataFrameObjective(
        frame,
        "random_intercept",
        columns={"y": "y", "group": "latent_group"},
        group_col="unit",
        order_cols=["ordinal"],
    ) as objective:
        actual = objective.evaluate(theta)
        expected = laplace_oracle(
            [
                {"row_id": str(i), "group_id": group, "y": value}
                for i, (group, _, value) in enumerate(records)
            ],
            theta,
        )
        np.testing.assert_allclose(
            [actual.value, *actual.gradient], [expected[0], *expected[1]], atol=1e-6, rtol=0
        )
        units = objective.units
    assert not units.is_cached
    expect_failure(lambda: objective.evaluate(theta), "closed", ModelContractError)
    expect_failure(
        lambda: DataFrameObjective(
            frame, "random_intercept", columns={"y": "y", "group": "latent_group"}, group_col="unit"
        ),
        "orderCols",
        ModelContractError,
    )
    tied = spark.createDataFrame(
        [("a", 1, 0.1), ("a", 1, 0.3)], "unit string, ordinal int, y double"
    ).withColumn("latent_group", lit(0))
    expect_failure(
        lambda: DataFrameObjective(
            tied,
            "random_intercept",
            columns={"y": "y", "group": "latent_group"},
            group_col="unit",
            order_cols=["ordinal"],
        ),
        "unique deterministic",
    )
    description = runtime.describe_prepared("random_intercept")
    model = TMBModel(
        modelId="random_intercept",
        parameters=theta,
        parameter_names=description["spec"]["fixed_parameters"],
        prepared=artifact_identity(description),
    )
    model.setParams(dataCols={"y": "y", "group": "latent_group"})
    expect_failure(lambda: model.transform(frame.drop("y")), "no declared", ModelContractError)
    return {
        "rows": actual.row_count,
        "value": actual.value,
        "gradient_max_abs_error": max(
            abs(a - b) for a, b in zip(actual.gradient, expected[1], strict=True)
        ),
    }


def main():
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("tmb-dataframe-ml-acceptance")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.task.maxFailures", "1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        with tempfile.TemporaryDirectory(prefix="tmb-ml-check-") as temporary:
            directory = Path(temporary)
            results = {
                "normal": check_normal(spark, directory),
                "regression": check_regression(spark, directory),
                "groups": check_groups(spark),
            }
        print(
            json.dumps(
                {
                    "case": "dataframe-ml",
                    "passed": True,
                    "spark_version": spark.version,
                    "checks": [
                        "shared-normal-mle",
                        "no-driver-raw-collect",
                        "caller-cache-preserved",
                        "response-free-normal-prediction",
                        "row-identity-and-schema",
                        "model-json-roundtrip",
                        "estimator-json-roundtrip",
                        "owned-model-overwrite",
                        "stale-artifact-refusal",
                        "vector-parameter-regression-mle",
                        "response-free-regression-prediction",
                        "pipeline-roundtrip",
                        "prediction-schema-refusal",
                        "complete-group-laplace-oracle",
                        "derived-cache-cleanup",
                        "explicit-order-required",
                        "duplicate-order-refusal",
                        "undeclared-prediction-refusal",
                    ],
                    "results": results,
                    "execution": "actual local[2] Spark, native R/TMB, SciPy driver and PySpark ML",
                    "global_row_order_promised": False,
                    "remote_cluster_executed": False,
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
