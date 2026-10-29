"""Actual prepared-model gradients, shared Spark objective and independent fits."""

from __future__ import annotations

import json
import math

from spark_tmb import ModelContractError, SparkTMBObjective, evaluate_prepared
from spark_tmb.fixed_bridge import laplace_oracle, normal_oracle

from examples import fixture


def assert_close(actual, expected, tolerance=2e-6):
    if max(abs(a - b) for a, b in zip(actual, expected, strict=True)) > tolerance:
        raise AssertionError((actual, expected))


def main():
    from pyspark.sql import SparkSession

    rows = fixture()
    theta = [0.4, math.log(1.2)]
    data = {"y": [row["y"] for row in rows]}
    local = evaluate_prepared("normal_mean", data, theta)
    value, gradient = normal_oracle(rows, theta)
    assert_close([local["value"], *local["gradient"]], [value, *gradient])
    finite_difference = []
    for i in range(2):
        plus, minus = theta.copy(), theta.copy()
        plus[i] += 1e-5
        minus[i] -= 1e-5
        finite_difference.append(
            (
                evaluate_prepared("normal_mean", data, plus)["value"]
                - evaluate_prepared("normal_mean", data, minus)["value"]
            )
            / 2e-5
        )
    assert_close(local["gradient"], finite_difference)
    random_theta = [0.7, math.log(0.8), math.log(0.5)]
    random_data = {**data, "group": [i // 3 for i in range(len(rows))]}
    local_random = evaluate_prepared("random_intercept", random_data, random_theta)
    expected_random = laplace_oracle(rows, random_theta)
    assert_close(
        [local_random["value"], *local_random["gradient"]],
        [expected_random[0], *expected_random[1]],
    )
    rejected = []
    for label, model, payload, parameters in [
        ("unprepared", "unprepared", data, theta),
        ("dimension", "normal_mean", data, [0]),
        ("nonfinite-objective", "normal_mean", data, [0, 1000]),
    ]:
        try:
            evaluate_prepared(model, payload, parameters)
        except ModelContractError:
            rejected.append(label)
        else:
            raise AssertionError("Invalid prepared request accepted: " + label)
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("ds60-prepared-tmb")
        .config("spark.ui.enabled", "false")
        .config("spark.task.maxFailures", "1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        units = [
            {"unit_id": f"g{i // 3}", "data": {"y": [row["y"] for row in rows[i : i + 3]]}}
            for i in range(0, len(rows), 3)
        ]
        rdd = spark.sparkContext.parallelize(units, 2).cache()
        objective = SparkTMBObjective(rdd, "normal_mean")
        global_result = objective.evaluate(theta)
        assert_close([global_result.value, *global_result.gradient], [value, *gradient])
        fits = objective.fit_independent_units([0, 0])
        expected = {unit["unit_id"]: sum(unit["data"]["y"]) / 3 for unit in units}
        for result in fits:
            assert_close(
                [result["fit"]["fitted_parameters"][0]], [expected[result["unit_id"]]], 1e-4
            )
        latent_units = [
            {"unit_id": unit["unit_id"], "data": {**unit["data"], "group": [0, 0, 0]}}
            for unit in units
        ]
        marginal = SparkTMBObjective(
            spark.sparkContext.parallelize(latent_units, 2), "random_intercept"
        )
        marginal_result = marginal.evaluate(random_theta)
        assert_close(
            [marginal_result.value, *marginal_result.gradient],
            [expected_random[0], *expected_random[1]],
        )
        print(
            json.dumps(
                {
                    "case": "registered-models",
                    "spark": spark.version,
                    "normal_gradient_error": max(
                        abs(a - b)
                        for a, b in zip(local["gradient"], finite_difference, strict=True)
                    ),
                    "laplace_gradient_error": max(
                        abs(a - b)
                        for a, b in zip(marginal_result.gradient, expected_random[1], strict=True)
                    ),
                    "shared_rows": global_result.row_count,
                    "independent_fits": fits,
                    "rejected": rejected,
                    "abi": local["abi"],
                    "execution": (
                        "compiled registered models in real local[2] Spark tasks; no remote cluster"
                    ),
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
