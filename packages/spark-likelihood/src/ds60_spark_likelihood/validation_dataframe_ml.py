"""Installed-wheel native Spark DataFrame/ML acceptance, with no R or classroom."""

from __future__ import annotations

import json
import math
import platform
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from .contracts import ObjectiveError
from .registry import RegisteredModel, register_model_factory, resolve_model
from .torch_backend import TorchLoss


def no_prediction_factory(config):
    from .models import normal_mean_loss

    if config:
        raise ObjectiveError("This validation model has no configuration")
    return RegisteredModel(
        TorchLoss("normal_without_prediction", 2, 0, normal_mean_loss), ("mu", "log_sigma"), ()
    )


def expect_failure(call, message):
    try:
        call()
    except Exception as error:
        if message not in str(error):
            raise AssertionError(f"Unexpected failure: {error}") from error
    else:
        raise AssertionError(f"Expected failure containing {message}")


def check_rows(spark, directory):
    import numpy as np

    from .dataframe import fit_independent_groups
    from .ml import SparkLikelihoodEstimator, SparkLikelihoodModel

    for option in ("tol", "l2Strength"):
        expect_failure(
            lambda name=option: SparkLikelihoodEstimator(**{name: 2**53 + 1}),
            "not exactly representable",
        )
    exact_options = SparkLikelihoodEstimator(tol=2**54, l2Strength=1.5)
    assert exact_options.getOrDefault("tol") == float(2**54)
    assert exact_options.getOrDefault("l2Strength") == 1.5
    values = [-1.0, 0.0, 1.0, 2.0, 4.0, 5.0]
    training = (
        spark.createDataFrame(
            [(f"r{i}", y, 1.0 + (i % 2)) for i, y in enumerate(values)],
            "row_id string, label double, observation_weight double",
        )
        .repartition(2)
        .cache()
    )
    try:
        training.count()
        estimator = SparkLikelihoodEstimator(
            modelId="normal_mean",
            featureCols={},
            labelCol="label",
            initialParameters=[0.0, math.log(2.0)],
            parameterBounds=[[-10.0, 10.0], [-5.0, 5.0]],
            tol=1e-5,
            maxIter=80,
        )
        with patch.object(
            type(training), "collect", side_effect=AssertionError("Raw observations reached driver")
        ):
            fitted = estimator.fit(training)
        assert training.is_cached
        mean = sum(values) / len(values)
        sd = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        np.testing.assert_allclose(fitted.parameters, [mean, math.log(sd)], atol=1e-4, rtol=0)
        future = spark.createDataFrame(
            [("b", "keep-b"), ("a", "keep-a")], "row_id string, note string"
        )
        predicted = fitted.transform(future)
        assert predicted.columns == ["row_id", "note", "prediction"]
        rows = {row.row_id: (row.note, row.prediction) for row in predicted.collect()}
        assert rows["a"][0] == "keep-a" and rows["b"][0] == "keep-b"
        np.testing.assert_allclose([rows["a"][1], rows["b"][1]], [mean, mean], atol=1e-4, rtol=0)
        path = directory / "normal-model"
        fitted.save(str(path))
        loaded = SparkLikelihoodModel.load(str(path))
        assert loaded.parameters == fitted.parameters and loaded.transform(future).count() == 2
        fitted.write().overwrite().save(str(path))
        estimator_path = directory / "normal-estimator"
        estimator.save(str(estimator_path))
        assert (
            SparkLikelihoodEstimator.load(str(estimator_path)).getOrDefault("labelCol") == "label"
        )
        payload = json.loads((path / "model.json").read_text())
        payload["descriptor"]["fingerprint"] = "0" * 64
        (path / "model.json").write_text(json.dumps(payload))
        expect_failure(lambda: SparkLikelihoodModel.load(str(path)), "fingerprint")
        grouped = spark.createDataFrame(
            [("a", v) for v in (-1.0, 0.0, 1.0)] + [("b", v) for v in (3.0, 4.0, 6.0, 7.0)],
            "unit string, y double",
        ).repartition(2)
        separate = fit_independent_groups(
            grouped,
            "normal_mean",
            [1.0, math.log(2.0)],
            feature_columns={},
            label_col="y",
            group_col="unit",
            bounds=[[-10.0, 10.0], [-5.0, 5.0]],
            tolerance=1e-5,
            max_iterations=80,
        )
        independent = {row.group_id: row for row in separate.collect()}
        np.testing.assert_allclose(
            [independent["a"].parameters[0], independent["b"].parameters[0]],
            [0.0, 5.0],
            atol=1e-4,
            rtol=0,
        )
        assert independent["a"].row_count == 3 and independent["b"].row_count == 4
        return {
            "parameters": list(fitted.parameters),
            "score": fitted.fit_summary["projected_gradient_inf_norm"],
            "independent_group_means": {key: row.parameters[0] for key, row in independent.items()},
        }
    finally:
        training.unpersist()


def check_regression_and_custom(spark, directory):
    import numpy as np
    from pyspark.ml import Pipeline, PipelineModel

    from .example_models import quadratic_model
    from .ml import SparkLikelihoodEstimator, SparkLikelihoodModel

    x = np.arange(-2.0, 6.0)
    noise = np.array([0.2, -0.1, 0.1, -0.2, 0.1, -0.1, 0.15, -0.15])
    y = 1.5 + 0.8 * x + noise
    frame = spark.createDataFrame(
        [(int(i), 1.0, float(a), float(b)) for i, (a, b) in enumerate(zip(x, y, strict=True))],
        "row_id int, intercept double, feature double, response double",
    ).repartition(2)
    estimator = SparkLikelihoodEstimator(
        modelId="linear_gaussian",
        modelConfig={"feature_count": 2},
        featureCols={"x0": "intercept", "x1": "feature"},
        labelCol="response",
        initialParameters=[0.0, 0.0, 0.0],
        parameterBounds=[[-10.0, 10.0], [-10.0, 10.0], [-5.0, 3.0]],
        tol=1e-5,
        maxIter=100,
    )
    pipeline = Pipeline(stages=[estimator]).fit(frame)
    fitted = pipeline.stages[0]
    expected = np.linalg.lstsq(np.column_stack([np.ones(len(x)), x]), y, rcond=None)[0]
    expected_scale = math.sqrt(float(np.mean((y - expected[0] - expected[1] * x) ** 2)))
    np.testing.assert_allclose(
        fitted.parameters, [*expected, math.log(expected_scale)], atol=1e-4, rtol=0
    )
    future = spark.createDataFrame(
        [(20, 1.0, -3.0), (19, 1.0, 6.0)], "row_id int, intercept double, feature double"
    )
    outputs = {row.row_id: row.prediction for row in pipeline.transform(future).collect()}
    np.testing.assert_allclose(
        [outputs[20], outputs[19]],
        [expected[0] - 3 * expected[1], expected[0] + 6 * expected[1]],
        atol=1e-4,
        rtol=0,
    )
    path = directory / "pipeline"
    pipeline.save(str(path))
    loaded = PipelineModel.load(str(path))
    restored = {row.row_id: row.prediction for row in loaded.transform(future).collect()}
    np.testing.assert_allclose(
        [restored[20], restored[19]], [outputs[20], outputs[19]], atol=1e-12, rtol=0
    )
    expect_failure(lambda: fitted.transform(future.drop("feature")), "numeric Spark column")
    # Registration is deliberately driver-only. Workers receive the resolved model.
    register_model_factory("quadratic_mean", quadratic_model, replace_existing=True)
    times = [-2.0, -1.0, 0.0, 1.0, 2.0]
    errors = [0.1, -0.1, 0.0, 0.1, -0.1]
    custom_data = spark.createDataFrame(
        [(t, 1.2 + 0.6 * t * t + e) for t, e in zip(times, errors, strict=True)],
        "time double, y double",
    ).repartition(2)
    custom = SparkLikelihoodEstimator(
        modelId="quadratic_mean",
        modelConfig={"sigma": 0.5},
        featureCols={"time": "time"},
        labelCol="y",
        initialParameters=[0.0, 0.0],
        tol=1e-5,
    ).fit(custom_data)
    np.testing.assert_allclose(custom.parameters, [1.2, 0.6], atol=1e-4, rtol=0)
    unlabeled = spark.createDataFrame([(3.0,), (-3.0,)], "time double")
    np.testing.assert_allclose(
        [row.prediction for row in custom.transform(unlabeled).collect()],
        [6.6, 6.6],
        atol=1e-4,
        rtol=0,
    )
    custom_path = directory / "custom-model"
    custom.save(str(custom_path))
    assert SparkLikelihoodModel.load(str(custom_path)).parameters == custom.parameters
    register_model_factory(
        "normal_without_prediction", no_prediction_factory, replace_existing=True
    )
    missing = resolve_model("normal_without_prediction")
    no_prediction = SparkLikelihoodModel(
        modelId=missing.model_id,
        parameters=[0.0, 0.0],
        parameter_names=missing.parameter_names,
        descriptor=missing.descriptor(),
    )
    expect_failure(lambda: no_prediction.transform(unlabeled), "does not declare")
    return {
        "parameters": list(fitted.parameters),
        "coefficient_oracle": expected.tolist(),
        "score": fitted.fit_summary["projected_gradient_inf_norm"],
        "custom_parameters": list(custom.parameters),
    }


def check_complete_units(spark, directory):
    import numpy as np

    from .dataframe import DataFrameObjective
    from .ml import SparkLikelihoodEstimator, SparkLikelihoodModel
    from .validation_units import rank_one_oracle

    centers = [-1.2, -0.8, -0.4, 0.0, 0.2, 0.7, 1.0, 1.3]
    offsets = [-0.2, -0.1, 0.0, 0.1, 0.2]
    records = [
        (f"g{g}", j, 3.0 + center + offset, 1.0)
        for g, center in enumerate(centers)
        for j, offset in enumerate(offsets)
    ]
    frame = spark.createDataFrame(
        records, "group_id string, ordinal int, y double, unit_weight double"
    ).repartition(2)
    theta = [3.0, math.log(0.4), math.log(0.5)]
    with DataFrameObjective(
        frame,
        "gaussian_random_intercept",
        feature_columns={},
        label_col="y",
        group_col="group_id",
        order_cols=["ordinal"],
        unit_weight_col="unit_weight",
    ) as objective:
        actual = objective.evaluate(theta)
        pieces = [
            rank_one_oracle([3.0 + center + offset for offset in offsets], theta)
            for center in centers
        ]
        expected = [
            sum(piece[0] for piece in pieces),
            *[sum(piece[1][j] for piece in pieces) for j in range(3)],
        ]
        np.testing.assert_allclose([actual.value, *actual.gradient], expected, atol=1e-8, rtol=0)
        assert actual.unit_count == 8 and actual.row_count == 40 and actual.weight_sum == 8.0
        backend = objective.backend
    assert not backend._units.is_cached
    expect_failure(lambda: objective.evaluate(theta), "closed")
    estimator = SparkLikelihoodEstimator(
        modelId="gaussian_random_intercept",
        featureCols={},
        labelCol="y",
        groupCol="group_id",
        orderCols=["ordinal"],
        unitWeightCol="unit_weight",
        initialParameters=theta,
        parameterBounds=[[0.0, 6.0], [-6.0, 2.0], [-6.0, 2.0]],
        tol=1e-5,
        maxIter=120,
    )
    fitted = estimator.fit(frame)
    variance = [math.exp(2 * fitted.parameters[1]), math.exp(2 * fitted.parameters[2])]
    np.testing.assert_allclose(
        [fitted.parameters[0], *variance], [3.1, 0.025, 0.6675], atol=1e-4, rtol=0
    )
    assert fitted.fit_summary["unit_count"] == 8 and fitted.fit_summary["row_count"] == 40
    future = spark.createDataFrame([("new-b",), ("new-a",)], "entity string")
    predicted = fitted.transform(future)
    assert predicted.schema["prediction"].metadata["target"] == "new_group_mean"
    np.testing.assert_allclose(
        [row.prediction for row in predicted.collect()], [3.1, 3.1], atol=1e-4, rtol=0
    )
    path = directory / "joint-model"
    fitted.save(str(path))
    assert SparkLikelihoodModel.load(str(path)).parameters == fitted.parameters
    wrong = fitted.copy({fitted.predictionTarget: "conditional_group_mean"})
    expect_failure(lambda: wrong.transform(future), "does not declare")
    tied = spark.createDataFrame([("a", 1, 0.1, 1.0), ("a", 1, 0.3, 1.0)], frame.schema)
    expect_failure(
        lambda: DataFrameObjective(
            tied,
            "gaussian_random_intercept",
            feature_columns={},
            label_col="y",
            group_col="group_id",
            order_cols=["ordinal"],
        ),
        "ordering keys must be unique",
    )
    weights = spark.createDataFrame([("a", 1, 0.1, 1.0), ("a", 2, 0.3, 2.0)], frame.schema)
    expect_failure(
        lambda: DataFrameObjective(
            weights,
            "gaussian_random_intercept",
            feature_columns={},
            label_col="y",
            group_col="group_id",
            unit_weight_col="unit_weight",
        ),
        "constant within",
    )
    expect_failure(
        lambda: DataFrameObjective(
            frame,
            "gaussian_random_intercept",
            feature_columns={},
            label_col="y",
            group_col="group_id",
            weight_col="unit_weight",
        ),
        "not observation weights",
    )
    unequal = [[0.1, 0.4], [1.0, 1.2, 1.4], [2.0, 2.4, 2.7, 2.9]]
    weights = [1.0, 2.0, 0.5]
    weighted = spark.createDataFrame(
        [
            (f"u{g}", j, value, weights[g])
            for g, unit in enumerate(unequal)
            for j, value in enumerate(unit)
        ],
        frame.schema,
    )
    with DataFrameObjective(
        weighted,
        "gaussian_random_intercept",
        feature_columns={},
        label_col="y",
        group_col="group_id",
        unit_weight_col="unit_weight",
        reduction="weighted_mean",
    ) as objective:
        result = objective.evaluate([0.7, math.log(0.8), math.log(0.5)])
        references = [
            rank_one_oracle(unit, [0.7, math.log(0.8), math.log(0.5)]) for unit in unequal
        ]
        expected_mean = sum(
            w * reference[0] for w, reference in zip(weights, references, strict=True)
        ) / sum(weights)
        np.testing.assert_allclose(result.value, expected_mean, atol=1e-8, rtol=0)
        assert result.weight_sum == 3.5 and result.unit_count == 3 and result.row_count == 9
    return {
        "parameters": list(fitted.parameters),
        "variance_estimates": variance,
        "balanced_oracle": [3.1, 0.025, 0.6675],
        "score": fitted.fit_summary["projected_gradient_inf_norm"],
        "unit_count": 8,
        "row_count": 40,
        "unequal_unit_weight_sum": result.weight_sum,
    }


def check_custom_count_units(spark, directory):
    """Custom non-Gaussian complete-unit model with a nonempty feature mapping."""
    import numpy as np

    from .dataframe import DataFrameObjective
    from .example_gamma_poisson import gamma_poisson_model
    from .ml import SparkLikelihoodEstimator, SparkLikelihoodModel
    from .optimization import minimize_lbfgsb
    from .validation_gamma_poisson import fixture, oracle_evaluation

    register_model_factory("gamma_poisson_shared_rate", gamma_poisson_model, replace_existing=True)
    units = fixture()
    records = [
        (unit.unit_id, i, float(exposure), int(count))
        for unit in units
        for i, (exposure, count) in enumerate(unit.rows)
    ]
    frame = spark.createDataFrame(
        records, "group_id string, ordinal int, opportunity double, count long"
    ).repartition(2)
    initial = [math.log(1.7), math.log(0.9)]
    bounds = [(-6.0, 6.0), (-6.0, 6.0)]
    expected = oracle_evaluation(units, initial)
    with DataFrameObjective(
        frame,
        "gamma_poisson_shared_rate",
        feature_columns={"exposure": "opportunity"},
        label_col="count",
        group_col="group_id",
        order_cols=["ordinal"],
    ) as objective:
        actual = objective.evaluate(initial)
        np.testing.assert_allclose(
            [actual.value, *actual.gradient],
            [expected.value, *expected.gradient],
            atol=1e-9,
            rtol=0,
        )
        assert actual.unit_count == 6 and actual.row_count == 13
    reference = minimize_lbfgsb(
        lambda theta: oracle_evaluation(units, theta), initial, bounds=bounds, max_iterations=80
    )
    assert reference.converged
    fitted = SparkLikelihoodEstimator(
        modelId="gamma_poisson_shared_rate",
        featureCols={"exposure": "opportunity"},
        labelCol="count",
        groupCol="group_id",
        orderCols=["ordinal"],
        initialParameters=initial,
        parameterBounds=bounds,
        maxIter=80,
        tol=1e-6,
    ).fit(frame)
    np.testing.assert_allclose(fitted.parameters, reference.parameters, atol=2e-5, rtol=0)
    future = spark.createDataFrame([("a", 0.5), ("b", 2.0)], "entity string, opportunity double")
    predictions = fitted.transform(future)
    assert predictions.schema["prediction"].metadata["target"] == "new_group_expected_count"
    output = {row.entity: row.prediction for row in predictions.collect()}
    rate = math.exp(fitted.parameters[0] - fitted.parameters[1])
    np.testing.assert_allclose(
        [output["a"], output["b"]], [0.5 * rate, 2 * rate], atol=1e-10, rtol=0
    )
    path = directory / "custom-count-model"
    fitted.save(str(path))
    assert SparkLikelihoodModel.load(str(path)).parameters == fitted.parameters
    return {
        "model_id": "gamma_poisson_shared_rate",
        "unit_count": actual.unit_count,
        "row_count": actual.row_count,
        "parameters": list(fitted.parameters),
        "value_gradient_oracle_error": max(
            abs(actual.value - expected.value),
            *(abs(a - b) for a, b in zip(actual.gradient, expected.gradient, strict=True)),
        ),
        "serial_fit_parameter_error": max(
            abs(a - b) for a, b in zip(fitted.parameters, reference.parameters, strict=True)
        ),
        "score": fitted.fit_summary["projected_gradient_inf_norm"],
        "prediction_target": "new_group_expected_count",
        "predictions": output,
    }


def main(require_installed=True):
    import scipy
    import torch
    from pyspark.sql import SparkSession

    import ds60_spark_likelihood as package

    package_path = Path(package.__file__).resolve()
    if require_installed:
        assert "site-packages" in package_path.parts, package_path
    assert shutil.which("R") is None and shutil.which("Rscript") is None
    assert not any(name == "ds60sqlpy" or name.startswith("ds60sqlpy.") for name in sys.modules)
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("standalone-likelihood-ml")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.task.maxFailures", "1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        with tempfile.TemporaryDirectory(prefix="likelihood-ml-") as temporary:
            directory = Path(temporary)
            results = {
                "rows": check_rows(spark, directory),
                "regression_custom": check_regression_and_custom(spark, directory),
                "complete_units": check_complete_units(spark, directory),
                "custom_count_units": check_custom_count_units(spark, directory),
            }
        report = {
            "kind": "package-dataframe-ml",
            "case": "dataframe-ml",
            "passed": True,
            "checks": [
                "ml-option-inexact-integer-refusal",
                "ml-option-exact-integer-float-acceptance",
                "shared-normal-mle",
                "no-raw-driver-collect",
                "caller-cache-preserved",
                "row-identity-schema",
                "response-free-row-prediction",
                "model-json-roundtrip",
                "estimator-json-roundtrip",
                "owned-overwrite",
                "stale-fingerprint-refusal",
                "linear-mle-oracle",
                "pipeline-roundtrip",
                "driver-only-custom-factory",
                "custom-label-free-prediction",
                "undeclared-prediction-refusal",
                "independent-group-fits-separate",
                "joint-gaussian-value-gradient-oracle",
                "balanced-joint-mle-oracle",
                "unit-row-count-distinction",
                "new-group-mean-label",
                "joint-json-roundtrip",
                "conditional-group-prediction-refusal",
                "complete-order-tie-refusal",
                "unit-weight-constant-refusal",
                "row-unit-weight-separation",
                "unit-weighted-mean-denominator",
                "derived-cache-cleanup",
                "custom-complete-unit-feature-mapping",
                "custom-unit-scipy-value-gradient-oracle",
                "custom-unit-serial-fit-oracle",
                "custom-unit-response-free-count-prediction",
                "custom-unit-json-roundtrip",
            ],
            "runtime": {
                "spark": spark.version,
                "torch": torch.__version__,
                "scipy": scipy.__version__,
                "package": package.__version__,
                "architecture": platform.machine(),
            },
            "installed_package_path": str(package_path),
            "results": results,
            "r_required": False,
            "classroom_imported": False,
            "global_order_promised": False,
            "remote_cluster_executed": False,
        }
        print(json.dumps(report, sort_keys=True, allow_nan=False))
        return report
    finally:
        spark.stop()
