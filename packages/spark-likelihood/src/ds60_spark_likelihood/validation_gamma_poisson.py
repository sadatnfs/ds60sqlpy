"""Independent SciPy oracles and serial/distributed fits for a custom unit model."""

from __future__ import annotations

import json
import math

from .contracts import ObjectiveError, PartitionSummary, combine_summaries, parameter_digest
from .example_gamma_poisson import gamma_poisson_model
from .optimization import minimize_lbfgsb
from .prediction import predict_batch
from .registry import register_model_factory, resolve_model
from .unit_backend import CompleteUnit, evaluate_units


def fixture():
    groups = [
        ([0, 0], [1.0, 2.0]),
        ([1, 0], [0.5, 1.5]),
        ([2, 4], [1.0, 2.0]),
        ([8, 5], [1.0, 1.0]),
        ([1, 2, 0], [2.0, 0.5, 1.0]),
        ([12, 4], [1.0, 0.5]),
    ]
    return [
        CompleteUnit(f"count-group-{i}", [(e, y) for y, e in zip(counts, exposure, strict=True)])
        for i, (counts, exposure) in enumerate(groups)
    ]


def scipy_oracle(unit, parameters):
    from scipy.special import digamma, gammaln

    alpha, beta = math.exp(parameters[0]), math.exp(parameters[1])
    total = math.fsum(row[1] for row in unit.rows)
    exposure = math.fsum(row[0] for row in unit.rows)
    denominator = beta + exposure
    value = (
        float(gammaln(alpha) - gammaln(alpha + total))
        - alpha * math.log(beta)
        + (alpha + total) * math.log(denominator)
        - math.fsum(y * math.log(e) - float(gammaln(y + 1)) for e, y in unit.rows)
    )
    gradient = (
        alpha
        * (float(digamma(alpha) - digamma(alpha + total)) - math.log(beta) + math.log(denominator)),
        -alpha + (alpha + total) * beta / denominator,
    )
    return value, gradient


def oracle_evaluation(units, parameters):
    results = [scipy_oracle(unit, parameters) for unit in units]
    summary = PartitionSummary(
        0,
        parameter_digest(parameters),
        "gamma_poisson_shared_rate",
        sum(len(unit.rows) for unit in units),
        float(len(units)),
        math.fsum(result[0] for result in results),
        tuple(math.fsum(result[1][j] for result in results) for j in range(2)),
    )
    return combine_summaries(
        [summary],
        parameters=parameters,
        model_id=summary.model_id,
        expected_partitions=1,
        expected_rows=summary.row_count,
    )


def resolved():
    register_model_factory("gamma_poisson_shared_rate", gamma_poisson_model, replace_existing=True)
    return resolve_model("gamma_poisson_shared_rate")


def poisson_limit_checks():
    """Independent Poisson limiting law exposes cancelled large-shape scores."""
    model = resolved()
    errors = []
    for counts in ((0.0, 0.0), (1.0, 3.0), (4.0, 6.0)):
        unit = CompleteUnit("poisson-limit", list(zip((1.0, 2.0), counts, strict=True)))
        expected_value = math.fsum(e - y * math.log(e) + math.lgamma(y + 1) for e, y in unit.rows)
        score = 3.0 - math.fsum(counts)
        for log_rate in (40.0, 100.0, 300.0):
            actual = evaluate_units(0, [unit], (log_rate, log_rate), model.loss).summary
            errors.append(
                max(
                    abs(actual.value - expected_value),
                    abs(actual.gradient[0] - score),
                    abs(actual.gradient[1] + score),
                )
            )
    assert max(errors) < 1e-9
    return max(errors)


def numerical():
    limit_error = poisson_limit_checks()
    model, units = resolved(), fixture()
    parameters = (math.log(1.7), math.log(0.9))
    actual = evaluate_units(0, units, parameters, model.loss).summary
    expected = oracle_evaluation(units, parameters)
    error = max(
        abs(actual.value - expected.value),
        *(abs(a - b) for a, b in zip(actual.gradient, expected.gradient, strict=True)),
    )
    assert error < 1e-9
    bounds = [(-6, 6), (-6, 6)]
    reference_fit = minimize_lbfgsb(
        lambda theta: oracle_evaluation(units, theta), parameters, bounds=bounds, max_iterations=80
    )

    def torch_evaluation(theta):
        record = evaluate_units(0, units, theta, model.loss).summary
        return combine_summaries(
            [record],
            parameters=theta,
            model_id=model.model_id,
            expected_partitions=1,
            expected_rows=record.row_count,
        )

    fitted = minimize_lbfgsb(torch_evaluation, parameters, bounds=bounds, max_iterations=80)
    fit_error = max(
        abs(a - b) for a, b in zip(fitted.parameters, reference_fit.parameters, strict=True)
    )
    assert fitted.converged and reference_fit.converged and fit_error < 2e-5
    assert fitted.gradient_inf_norm < 1e-4
    predictions = predict_batch(model, parameters, [(1.0,), (2.0,)], "new_group_expected_count")
    assert (
        max(abs(a - b) for a, b in zip(predictions, [1.7 / 0.9, 2 * 1.7 / 0.9], strict=True))
        < 1e-12
    )
    joint = CompleteUnit("same-rate", [(1.0, 0.0), (1.0, 0.0)])
    split = [CompleteUnit("first-rate", [(1.0, 0.0)]), CompleteUnit("second-rate", [(1.0, 0.0)])]
    fixed = (math.log(2.0), 0.0)
    joint_loss = evaluate_units(0, [joint], fixed, model.loss).summary.value
    split_loss = evaluate_units(0, split, fixed, model.loss).summary.value
    assert abs(joint_loss - 2 * math.log(3)) < 1e-12 and abs(split_loss - 4 * math.log(2)) < 1e-12
    rejected = []
    for name, rows in [
        ("nonpositive-exposure", [(0.0, 1.0)]),
        ("fractional-count", [(1.0, 0.5)]),
        ("negative-count", [(1.0, -1.0)]),
        ("count-recurrence-bound", [(1.0, 10001.0)]),
    ]:
        try:
            evaluate_units(0, [CompleteUnit(name, rows)], parameters, model.loss)
        except ObjectiveError:
            rejected.append(name)
        else:
            raise AssertionError("Invalid Gamma-Poisson support was accepted")
    print(
        json.dumps(
            {
                "kind": "package-custom-gamma-poisson",
                "passed": True,
                "units": len(units),
                "rows": actual.row_count,
                "max_scipy_value_gradient_error": error,
                "max_poisson_limit_value_gradient_error": limit_error,
                "serial_fit_parameter_error": fit_error,
                "fitted_parameters": fitted.parameters,
                "gradient_inf_norm": fitted.gradient_inf_norm,
                "marginal_prediction_target": "new_group_expected_count",
                "rejected": rejected,
                "splitting_changes_likelihood": True,
                "r_required": False,
            },
            sort_keys=True,
        )
    )


def spark_check():
    from pyspark.sql import SparkSession

    from .spark_units import SparkUnitObjective

    spark = (
        SparkSession.builder.master("local[2]")
        .appName("custom-gamma-poisson-package")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        model, units = resolved(), fixture()
        initial = (math.log(1.7), math.log(0.9))
        bounds = [(-6, 6), (-6, 6)]
        reference = minimize_lbfgsb(
            lambda theta: oracle_evaluation(units, theta), initial, bounds=bounds, max_iterations=80
        )
        with SparkUnitObjective(spark.sparkContext.parallelize(units, 3), model.loss) as objective:
            actual = objective.evaluate(initial)
            expected = oracle_evaluation(units, initial)
            initial_error = max(
                abs(actual.value - expected.value),
                *(abs(a - b) for a, b in zip(actual.gradient, expected.gradient, strict=True)),
            )
            fitted = minimize_lbfgsb(objective.evaluate, initial, bounds=bounds, max_iterations=80)
        fit_error = max(
            abs(a - b) for a, b in zip(fitted.parameters, reference.parameters, strict=True)
        )
        assert (
            initial_error < 1e-9 and fit_error < 2e-5 and fitted.converged and reference.converged
        )
        assert fitted.gradient_inf_norm < 1e-4
        print(
            json.dumps(
                {
                    "kind": "package-spark-custom-unit",
                    "passed": True,
                    "spark": spark.version,
                    "model_id": model.model_id,
                    "units": len(units),
                    "rows": actual.row_count,
                    "max_scipy_value_gradient_error": initial_error,
                    "serial_fit_parameter_error": fit_error,
                    "parameters": fitted.parameters,
                    "gradient_inf_norm": fitted.gradient_inf_norm,
                    "r_required": False,
                    "remote_cluster_executed": False,
                },
                sort_keys=True,
            )
        )
    finally:
        spark.stop()
