"""Native local Spark tasks plus Torch AD with independent statistical oracles."""

from __future__ import annotations

import json
import math

from ds60_spark_likelihood import ObjectiveError
from ds60_spark_likelihood.models import logistic, normal_mean
from ds60_spark_likelihood.optimization import minimize_lbfgsb
from ds60_spark_likelihood.spark_backend import SparkObjective
from pyspark.sql import SparkSession


def close(actual, expected, tolerance=1e-8):
    assert math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (actual, expected)


def run():
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("ds60-additive-likelihood-check")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    results = []
    try:
        rows = [(1.0, y, w) for y, w in [(0.0, 1.0), (1.0, 3.0), (1.0, 2.0)]]
        for count in (1, 2, 5):
            source = spark.sparkContext.parallelize(rows, count)
            with SparkObjective(
                source, logistic(1), batch_size=1, reduction="weighted_mean"
            ) as obj:
                result = obj.evaluate((0.0,))
                close(result.value, math.log(2))
                close(result.gradient[0], -1 / 3)
                assert result.row_count == 3 and result.weight_sum == 6
                assert sum(obj.partition_rows) == 3
                results.append(
                    {
                        "partitions": count,
                        "partition_rows": obj.partition_rows,
                        "value": result.value,
                        "gradient": result.gradient,
                    }
                )
                if count == 2:
                    fitted = minimize_lbfgsb(obj.evaluate, (0.0,), bounds=((-10, 10),))
                    assert fitted.converged
                    close(fitted.parameters[0], math.log(5), tolerance=1e-6)
                    assert fitted.gradient_inf_norm < 1e-7
                    fit_report = {
                        "parameters": fitted.parameters,
                        "iterations": fitted.iterations,
                        "evaluations": fitted.objective_calls,
                        "gradient_inf_norm": fitted.gradient_inf_norm,
                    }
            assert not source.is_cached
            try:
                obj.evaluate((0.0,))
            except ObjectiveError:
                pass
            else:
                raise AssertionError("closed objective accepted work")

        frame = spark.createDataFrame([(1.0,), (2.0,), (4.0,), (7.0,)], ["y"]).repartition(2)
        with SparkObjective.from_dataframe(
            frame, normal_mean(), feature_columns=[], target_column="y", batch_size=2
        ) as normal:
            fitted = minimize_lbfgsb(normal.evaluate, (2.0, 1.0), bounds=((-20, 20), (-4, 4)))
            assert fitted.converged
            close(fitted.parameters[0], 3.5, tolerance=1e-6)
            close(fitted.parameters[1], math.log(math.sqrt(5.25)), tolerance=1e-6)
            normal_report = {
                "parameters": fitted.parameters,
                "gradient_inf_norm": fitted.gradient_inf_norm,
                "iterations": fitted.iterations,
                "evaluations": fitted.objective_calls,
            }

        bad = spark.createDataFrame([("1",), ("2",)], ["y"])
        try:
            SparkObjective.from_dataframe(bad, normal_mean(), feature_columns=[], target_column="y")
        except ObjectiveError:
            pass
        else:
            raise AssertionError("string input silently cast")

        # Keep the caller's separately cached source alive after owned cleanup.
        source = spark.sparkContext.parallelize(rows, 2).cache()
        source.count()
        with SparkObjective(source, logistic(1)) as obj:
            obj.evaluate((0.2,))
        assert source.is_cached
        source.unpersist(blocking=True)
        print(
            json.dumps(
                {
                    "kind": "spark-local-torch-additive-mle",
                    "passed": True,
                    "spark": spark.version,
                    "master": spark.sparkContext.master,
                    "partition_cases": results,
                    "weighted_logistic_fit": fit_report,
                    "normal_mle": normal_report,
                    "caller_cache_preserved": True,
                    "distributed_training_executed": False,
                    "multi_node_executed": False,
                },
                sort_keys=True,
            )
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    run()
