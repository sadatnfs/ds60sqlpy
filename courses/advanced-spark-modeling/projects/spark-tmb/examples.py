"""Fixed real Spark/R/TMB investigations with independent numeric references."""

from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import asdict
from functools import partial
from pathlib import Path

from spark_tmb.fixed_bridge import (
    ObjectiveError,
    PreparedTMB,
    bounded_rows,
    combine_results,
    laplace_oracle,
    normal_oracle,
    partition_result,
    request_for,
)


def fixture():
    return [
        {"row_id": f"r{i:02}", "group_id": f"g{i // 3}", "y": value}
        for i, value in enumerate([-1.1, -0.7, -0.2, 0.4, 0.6, 1.2, 1.7, 2.1, 2.4, 3.1, 3.4, 3.8])
    ]


def partition_callback(index, iterator, *, model, parameters, prepared):
    yield partition_result(index, iterator, model, parameters, prepared)


def evaluate(rdd, rows, model, parameters, prepared):
    records = rdd.mapPartitionsWithIndex(
        partial(partition_callback, model=model, parameters=parameters, prepared=prepared)
    ).collect()
    result = combine_results(
        records,
        parameters=parameters,
        model=model,
        expected_rows=rows,
        expected_partitions=rdd.getNumPartitions(),
    )
    return result, records


def assert_oracle(result, oracle, *, tolerance=2e-7):
    value, gradient = oracle
    error = abs(result.value - value)
    gradient_error = max(abs(a - b) for a, b in zip(result.gradient, gradient, strict=True))
    if error > tolerance or gradient_error > tolerance:
        raise AssertionError(
            f"Independent oracle mismatch: value={error}, gradient={gradient_error}"
        )
    return {"value_abs_error": error, "gradient_max_abs_error": gradient_error}


def spark_case(case):
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master("local[2]")
        .appName("ds60-spark-tmb-" + case)
        .config("spark.ui.enabled", "false")
        .config("spark.task.maxFailures", "1")
        .config("spark.python.worker.reuse", "true")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    prepared = PreparedTMB(
        os.environ.get("SPARK_TMB_PROJECT_ROOT", "/opt/spark-tmb"),
        os.environ.get("SPARK_TMB_BUILD_DIR", "/opt/spark-tmb-models"),
    )
    rows = bounded_rows(fixture())
    try:
        if case == "group-laplace":
            # Assign every complete independent group using a stable numeric suffix.
            rdd = (
                spark.sparkContext.parallelize(rows, 3)
                .keyBy(lambda row: row["group_id"])
                .partitionBy(3, lambda key: int(key[1:]))
                .values()
                .cache()
            )
            model, theta = "random_intercept", (0.7, math.log(0.8), math.log(0.5))
            result, records = evaluate(rdd, rows, model, theta, prepared)
            checks = assert_oracle(result, laplace_oracle(rows, theta))
            output = {
                "case": case,
                "target": "sum of independent Gaussian Laplace marginals",
                "mathematical_integral": "exact for these Gaussian latent intercepts",
                "result": asdict(result),
                "oracle": checks,
                "partitions": records,
            }
        elif case == "partition-normal":
            theta = (1.1, math.log(1.3))
            layouts = []
            for count in (2, 3):
                rdd = spark.sparkContext.parallelize(rows, count)
                result, records = evaluate(rdd, rows, "normal_mean", theta, prepared)
                layouts.append(
                    {
                        "partitions": count,
                        "result": asdict(result),
                        "oracle": assert_oracle(result, normal_oracle(rows, theta)),
                        "receipts": records,
                    }
                )
            output = {
                "case": case,
                "target": "one global additive normal likelihood",
                "layouts": layouts,
            }
        elif case == "global-normal-fit":
            rdd = spark.sparkContext.parallelize(rows, 3).cache()
            theta = (0.0, math.log(2.0))
            trace = []
            initial, _ = evaluate(rdd, rows, "normal_mean", theta, prepared)
            trace.append(asdict(initial))
            # Exact conditional updates for this normal model, derived from the
            # detached global AD score. This is not a general nonlinear solver.
            mu = theta[0] - initial.gradient[0] * math.exp(2 * theta[1]) / len(rows)
            middle, _ = evaluate(rdd, rows, "normal_mean", (mu, theta[1]), prepared)
            trace.append(asdict(middle))
            ratio = 1 - middle.gradient[1] / len(rows)
            if ratio <= 0:
                raise ObjectiveError("No interior positive-scale estimate")
            fitted = (mu, theta[1] + 0.5 * math.log(ratio))
            final, _ = evaluate(rdd, rows, "normal_mean", fitted, prepared)
            trace.append(asdict(final))
            expected_mu = math.fsum(row["y"] for row in rows) / len(rows)
            expected_sigma = math.sqrt(
                math.fsum((row["y"] - expected_mu) ** 2 for row in rows) / len(rows)
            )
            if abs(mu - expected_mu) > 1e-9 or abs(math.exp(fitted[1]) - expected_sigma) > 1e-9:
                raise AssertionError("Distributed fit differs from independent normal MLE")
            if max(map(abs, final.gradient)) > 1e-7:
                raise AssertionError("Distributed fit has a nonstationary final score")
            output = {
                "case": case,
                "estimator": "shared mean and scale, three distributed score evaluations",
                "fitted_parameters": fitted,
                "fitted_sigma": math.exp(fitted[1]),
                "oracle": assert_oracle(final, normal_oracle(rows, fitted)),
                "trace": trace,
            }
        else:
            raise ValueError("Unknown Spark/TMB case")
        output.update(
            spark_version=spark.version,
            execution="real Spark local[2] tasks with fresh R subprocesses",
            limitation="one native CPU container, no remote-cluster or performance claim",
        )
        print(json.dumps(output, sort_keys=True, allow_nan=False))
    finally:
        spark.stop()


def failure_contracts():
    rows = fixture()
    rejected = []
    tests = {
        "unknown-model": lambda: request_for("../../arbitrary", rows, [0, 0]),
        "nonfinite": lambda: request_for(
            "normal_mean", [{"row_id": "a", "group_id": "a", "y": math.nan}], [0, 0]
        ),
        "duplicate-row": lambda: request_for("normal_mean", [rows[0], rows[0]], [0, 0]),
        "singleton": lambda: request_for("normal_mean", rows[:1], [0, 0]),
        "wrong-dimension": lambda: request_for("normal_mean", rows, [0, 0, 0]),
    }
    for key, call in tests.items():
        try:
            call()
        except ObjectiveError:
            rejected.append(key)
        else:
            raise AssertionError("Invalid input accepted: " + key)
    # Real R process failures and stale/split summaries are also exercised by
    # the dedicated source/runtime test suite, not silently called passed here.
    print(
        json.dumps(
            {
                "case": "failure-contracts",
                "rejected": rejected,
                "execution": "Python boundary validation",
            }
        )
    )


def rpy2_frame():
    import contextlib
    import io
    import runpy

    root = Path(os.environ.get("TMB_PROJECT_ROOT", "/opt/tmb-project"))
    # The original TMB project's fixed test exercises scoped pandas conversion,
    # row order, OLS oracle, bad inputs and detached return values in real R.
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        runpy.run_path(str(root / "tests/bridge_acceptance.py"), run_name="__main__")
    rows = [json.loads(line) for line in output.getvalue().splitlines() if line.startswith("{")]
    if len(rows) != 1 or rows[0].get("status") != "passed":
        raise AssertionError("The fixed rpy2 probe did not emit its complete acceptance result")
    print(json.dumps({"case": "rpy2-frame", **rows[0]}, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    case = sys.argv[1]
    if case == "failure-contracts":
        failure_contracts()
    elif case == "rpy2-frame":
        rpy2_frame()
    else:
        spark_case(case)
