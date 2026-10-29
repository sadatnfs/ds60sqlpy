"""Complete bounded examples for custom Spark/Torch likelihood work."""

from __future__ import annotations

import argparse
import json
import math

import numpy as np
import pandas as pd
import torch
from ds60_spark_likelihood import combine_summaries
from ds60_spark_likelihood.integrations.distributed_cases import sampler_audit
from ds60_spark_likelihood.models import logistic, nonlinear_gaussian, normal_mean
from ds60_spark_likelihood.optimization import minimize_lbfgsb
from ds60_spark_likelihood.spark_backend import SparkObjective
from ds60_spark_likelihood.torch_backend import evaluate_partition
from pyspark.sql import SparkSession
from scipy.optimize import minimize


def additive(spark):
    rows = [(1.0, 0.0, 1.0), (1.0, 1.0, 3.0), (1.0, 1.0, 2.0)]
    with SparkObjective(
        spark.sparkContext.parallelize(rows, 2), logistic(1), reduction="weighted_mean"
    ) as objective:
        fit = minimize_lbfgsb(objective.evaluate, (0.0,), bounds=((-10, 10),))
        assert fit.converged and abs(fit.parameters[0] - math.log(5)) < 1e-6
        return {
            "kind": "weighted-logistic-global-mle",
            "passed": True,
            "rows": objective.row_count,
            "partition_rows": objective.partition_rows,
            "coefficient": fit.parameters[0],
            "analytic_log_odds": math.log(5),
            "gradient_inf_norm": fit.gradient_inf_norm,
            "iterations": fit.iterations,
            "weighted_probability": 5 / 6,
            "independent_group_fits": False,
        }


def nonlinear(spark):
    times = np.linspace(0, 8, 40)
    observations = 3 * np.exp(-0.6 * times) + 1 + np.tile([-0.03, 0.01, 0.02, -0.01, 0.01], 8)
    rows = [(float(t), float(y), 1.0) for t, y in zip(times, observations, strict=True)]
    initial = (2.5, math.log(0.5), 0.9, math.log(0.1))
    bounds = ((0.1, 6), (-3, 1), (-2, 3), (-6, 1))

    def serial(values):
        a, log_rate, baseline, log_scale = values
        residual = observations - (a * np.exp(-np.exp(log_rate) * times) + baseline)
        return float(
            np.sum(
                log_scale + 0.5 * (residual / np.exp(log_scale)) ** 2 + 0.5 * math.log(2 * math.pi)
            )
        )

    independent = minimize(
        serial,
        initial,
        method="L-BFGS-B",
        bounds=bounds,
        options={"ftol": 1e-13, "gtol": 1e-6, "maxiter": 200},
    )
    assert independent.success
    with SparkObjective(
        spark.sparkContext.parallelize(rows, 3), nonlinear_gaussian(), batch_size=8
    ) as objective:
        fit = minimize_lbfgsb(
            objective.evaluate, initial, bounds=bounds, max_iterations=200, function_tolerance=1e-13
        )
        assert fit.converged
        error = float(np.max(np.abs(np.asarray(fit.parameters) - independent.x)))
        assert error < 2e-4
        assert fit.gradient_inf_norm < 1e-3
        a, log_rate, baseline, log_scale = fit.parameters
        prediction = a * math.exp(-math.exp(log_rate) * 9) + baseline
        return {
            "kind": "nonlinear-gaussian-global-mle",
            "passed": True,
            "rows": objective.row_count,
            "partition_rows": objective.partition_rows,
            "parameters": fit.parameters,
            "serial_parameter_max_error": error,
            "gradient_inf_norm": fit.gradient_inf_norm,
            "iterations": fit.iterations,
            "objective_evaluations": fit.objective_calls,
            "forecast_at_time_9": prediction,
            "noise_scale": math.exp(log_scale),
            "global_optimum_proven": False,
        }


def fit_group(frame):
    # applyInPandas receives a complete group. The fixture is explicitly bounded;
    # this check does not prevent an already-materialized giant group from OOM.
    assert 2 <= len(frame) <= 1000
    identifier = int(frame["group"].iloc[0])
    rows = [(float(y), 1.0) for y in frame["y"]]

    def objective(theta):
        summary = evaluate_partition(0, rows, theta, normal_mean())
        return combine_summaries(
            [summary],
            parameters=theta,
            model_id="normal_mean",
            expected_partitions=1,
            expected_rows=len(rows),
        )

    fit = minimize_lbfgsb(objective, (0.0, 0.0), bounds=((-20, 20), (-4, 4)))
    assert fit.converged
    return pd.DataFrame(
        {
            "group": [identifier],
            "rows": [len(rows)],
            "mu": [fit.parameters[0]],
            "sigma": [math.exp(fit.parameters[1])],
            "gradient_max": [fit.gradient_inf_norm],
        }
    )


def groups(spark):
    values = [
        (group, float(group * 2 + offset))
        for group in range(3)
        for offset in (-0.5, -0.2, 0.0, 0.1, 0.6)
    ]
    frame = spark.createDataFrame(values, ["group", "y"]).repartition(2)
    fitted = (
        frame.groupBy("group")
        .applyInPandas(
            fit_group, schema="group long, rows long, mu double, sigma double, gradient_max double"
        )
        .orderBy("group")
        .collect()
    )
    assert len(fitted) == 3 and sum(row.rows for row in fitted) == len(values)
    for row in fitted:
        assert abs(row.mu - row.group * 2) < 1e-6
        assert abs(row.sigma - math.sqrt(0.132)) < 1e-6
    return {
        "kind": "independent-group-mles",
        "passed": True,
        "input_rows": len(values),
        "fits": [row.asDict() for row in fitted],
        "shared_parameters": False,
        "whole_group_memory_required": True,
    }


def arrow(spark):
    source = spark.range(17).repartition(4)
    results = []
    expected = None
    for limit in (1, 3):
        spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", str(limit))

        def batches(iterator, limit=limit):
            for frame in iterator:
                assert len(frame) <= limit
                features = torch.tensor(frame["id"].to_numpy(), dtype=torch.float64)
                transformed = (features * features + 2).numpy()
                yield pd.DataFrame(
                    {
                        "id": frame["id"],
                        "transformed": transformed,
                        "batch_rows": [len(frame)] * len(frame),
                    }
                )

        output = (
            source.mapInPandas(batches, schema="id long, transformed double, batch_rows long")
            .orderBy("id")
            .collect()
        )
        assert [row.id for row in output] == list(range(17))
        assert all(row.transformed == row.id**2 + 2 for row in output)
        observed = [(row.id, row.transformed) for row in output]
        if expected is None:
            expected = observed
        else:
            assert observed == expected
        results.append(
            {
                "configured_batch_limit": limit,
                "max_observed_batch": max(row.batch_rows for row in output),
            }
        )
    return {
        "kind": "arrow-pandas-torch-batches",
        "passed": True,
        "rows": len(expected),
        "batch_cases": results,
        "batch_size_invariant": True,
        "raw_data_collected_only_for_tiny_test_oracle": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "case",
        choices=(
            "additive-logistic",
            "nonlinear-gaussian",
            "independent-groups",
            "arrow-batches",
            "sharding-audit",
        ),
    )
    args = parser.parse_args()
    if args.case == "sharding-audit":
        print(json.dumps(sampler_audit(), sort_keys=True))
        return
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("ds60-custom-model-case")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        function = {
            "additive-logistic": additive,
            "nonlinear-gaussian": nonlinear,
            "independent-groups": groups,
            "arrow-batches": arrow,
        }[args.case]
        result = function(spark)
        result.update(
            spark=spark.version,
            master=spark.sparkContext.master,
            multi_node_executed=False,
            gpu_executed=False,
        )
        print(json.dumps(result, sort_keys=True))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
