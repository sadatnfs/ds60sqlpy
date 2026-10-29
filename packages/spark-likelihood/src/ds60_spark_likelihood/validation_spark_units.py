"""Native local Spark complete-unit preservation and exact Gaussian group checks."""

from __future__ import annotations

import json
import math

from .contracts import ObjectiveError, PartitionSummary, combine_summaries, parameter_digest
from .optimization import minimize_lbfgsb
from .registry import resolve_model
from .spark_units import SparkUnitObjective
from .unit_backend import CompleteUnit
from .validation_units import rank_one_oracle


def run():
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master("local[2]")
        .appName("independent-package-unit-check")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        values = [[-0.1, 0.2], [1.1, 1.3, 0.8], [2.2, 2.7, 1.9, 2.3]]
        weights = [1.0, 2.0, 0.5]
        theta = (0.7, math.log(0.8), math.log(0.5))
        units = [
            CompleteUnit(f"g{i}", [(value,) for value in data], weight)
            for i, (data, weight) in enumerate(zip(values, weights, strict=True))
        ]
        model = resolve_model("gaussian_random_intercept").loss
        references = [rank_one_oracle(group, theta) for group in values]
        expected_value = (
            math.fsum(
                weight * result[0] for weight, result in zip(weights, references, strict=True)
            )
            / 3.5
        )
        expected_gradient = [
            math.fsum(
                weight * result[1][i] for weight, result in zip(weights, references, strict=True)
            )
            / 3.5
            for i in range(3)
        ]
        reports = []
        for partitions in (1, 2, 5):
            original = spark.sparkContext.parallelize(units, partitions).cache()
            with SparkUnitObjective(original, model, reduction="weighted_mean") as objective:
                result = objective.evaluate(theta)
                error = max(
                    abs(result.value - expected_value),
                    *(abs(a - b) for a, b in zip(result.gradient, expected_gradient, strict=True)),
                )
                assert (
                    error < 1e-9
                    and result.unit_count == 3
                    and result.row_count == 9
                    and result.weight_sum == 3.5
                )
                reports.append(
                    {
                        "partitions": partitions,
                        "error": error,
                        "unit_count": result.unit_count,
                        "row_count": result.row_count,
                    }
                )
            assert original.is_cached
            original.unpersist(blocking=True)
            try:
                objective.evaluate(theta)
            except ObjectiveError:
                pass
            else:
                raise AssertionError("closed complete-unit objective was reused")
        unweighted = [CompleteUnit(unit.unit_id, unit.rows) for unit in units]
        bounds = [(-5, 5), (-4, 2), (-4, 2)]
        with SparkUnitObjective(spark.sparkContext.parallelize(unweighted, 2), model) as objective:
            fitted = minimize_lbfgsb(
                objective.evaluate, theta, bounds=bounds, max_iterations=60, gradient_tolerance=1e-7
            )

        def oracle(parameters):
            pieces = [rank_one_oracle(group, parameters) for group in values]
            total = math.fsum(piece[0] for piece in pieces)
            gradient = tuple(math.fsum(piece[1][j] for piece in pieces) for j in range(3))
            summary = PartitionSummary(
                0, parameter_digest(parameters), model.model_id, 9, 3.0, total, gradient
            )
            return combine_summaries(
                [summary],
                parameters=parameters,
                model_id=model.model_id,
                expected_rows=9,
                expected_partitions=1,
            )

        reference_fit = minimize_lbfgsb(
            oracle, theta, bounds=bounds, max_iterations=60, gradient_tolerance=1e-7
        )
        fit_error = max(
            abs(a - b) for a, b in zip(fitted.parameters, reference_fit.parameters, strict=True)
        )
        assert fitted.converged and reference_fit.converged and fit_error < 2e-5
        assert (
            fitted.gradient_inf_norm < 1e-4 and getattr(fitted.evaluation, "unit_count", None) == 3
        )
        duplicate = spark.sparkContext.parallelize([units[0], units[0]], 2)
        try:
            SparkUnitObjective(duplicate, model)
        except ObjectiveError as error:
            assert "duplicate unit ID" in str(error)
        else:
            raise AssertionError("a split/duplicated group was accepted")
        print(
            json.dumps(
                {
                    "kind": "package-spark-units",
                    "passed": True,
                    "spark": spark.version,
                    "layouts": reports,
                    "shared_group_fit": {
                        "parameters": fitted.parameters,
                        "gradient_inf_norm": fitted.gradient_inf_norm,
                        "oracle_parameter_error": fit_error,
                        "objective_calls": fitted.objective_calls,
                    },
                    "duplicate_unit_rejected": True,
                    "caller_cache_preserved": True,
                    "closed_objective_rejected": True,
                    "raw_data_collected": False,
                    "r_required": False,
                    "execution": "native local[2], no remote-cluster claim",
                },
                sort_keys=True,
            )
        )
    finally:
        spark.stop()
