"""Actual installed-wheel Spark checks for the nine added 0.2 native models.

The two reference files are retained independent 70-digit mathematical outputs.
This program compares fixed-point values/scores and response-free moments. It
does not run an optimizer, sample a posterior or claim Hessian coverage.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import tempfile
from pathlib import Path

ROW_FIELDS = {
    "binomial_logistic": ["x", "trials", "y"],
    "beta_binomial": ["x", "trials", "y"],
    "beta_regression": ["x", "y"],
    "lognormal_regression": ["x", "y"],
    "student_t_regression": ["x", "y"],
    "zero_truncated_poisson": ["x", "exposure", "y"],
    "zero_inflated_poisson": ["x", "z", "exposure", "y"],
    "hurdle_poisson": ["x", "z", "exposure", "y"],
}
CORRELATED = "gaussian_correlated_random_slope"
MOMENT_COLUMNS = ["mean", "variance", "sd"]
RELATIVE_TOLERANCE = 3e-8
ABSOLUTE_TOLERANCE = 3e-7


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def close(actual, expected):
    expected = float(expected)
    require(
        type(actual) in (int, float)
        and math.isfinite(actual)
        and math.isfinite(expected)
        and math.isclose(
            actual, expected, rel_tol=RELATIVE_TOLERANCE, abs_tol=ABSOLUTE_TOLERANCE
        ),
        f"Expected {expected!r}, received {actual!r}",
    )


def selected_cases(rows_path, gaussian_path):
    """Keep two ordinary parameter points per row family and both exact groups."""
    rows = json.loads(Path(rows_path).read_text())
    gaussian = json.loads(Path(gaussian_path).read_text())
    result = []
    for family in ROW_FIELDS:
        matches = [
            case
            for case in rows["results"]
            if case["family"] == family
            and (
                case["case"] == "weighted_baseline"
                or case["case"].startswith("changed_")
            )
        ]
        require(len(matches) == 2, f"Expected baseline and changed point for {family}")
        require(
            matches[0]["parameters"] != matches[1]["parameters"],
            "Parameters did not change",
        )
        for case in matches:
            result.append((family, case, sha256(rows_path)))
    require(
        len(gaussian["results"]) == 2, "Expected two exact Gaussian conditioning cases"
    )
    result.extend(
        (CORRELATED, case, sha256(gaussian_path)) for case in gaussian["results"]
    )
    return result


def fixture_rows(model_id, case):
    """Build tiny explicit driver-side fixture records, never executor Python."""
    if model_id == CORRELATED:
        training = [
            {"row_id": i, "series": "g0", "x": row[0], "y": row[1]}
            for i, row in enumerate(case["history"])
        ]
        future = [
            {"row_id": 100 + i, "series": "g0", "x": value}
            for i, value in enumerate(case["future"])
        ]
    else:
        fields = ROW_FIELDS[model_id]
        training = []
        for i, (row, weight) in enumerate(
            zip(case["rows"], case["weights"], strict=True)
        ):
            require(len(row) == len(fields), "Reference training shape differs")
            training.append(
                {"row_id": i, **dict(zip(fields, row, strict=True)), "weight": weight}
            )
        future = []
        for i, row in enumerate(case["future"]):
            require(len(row) == len(fields) - 1, "Reference future shape differs")
            future.append(
                {"row_id": 100 + i, **dict(zip(fields[:-1], row, strict=True))}
            )
    require(all("y" not in row for row in future), "Future fixture contains a response")
    return training, future


def moments(case, target):
    if target == "response":
        values = case["prediction_and_forecast_moments"]
        return [
            [
                float(row["mean"]),
                float(row["variance"]),
                math.sqrt(float(row["variance"])),
            ]
            for row in values
        ]
    values = case[target]
    return [
        [
            float(mean),
            float(values["covariance"][i][i]),
            math.sqrt(float(values["covariance"][i][i])),
        ]
        for i, mean in enumerate(values["mean"])
    ]


def fixture_sql(rows):
    """Produce typed Spark SQL VALUES without Python executor functions."""
    require(bool(rows), "A typed fixture requires at least one source row")
    fields = list(rows[0])
    require(all(list(row) == fields for row in rows), "Fixture field order differs")

    def literal(value):
        if isinstance(value, str):
            return "'" + value.replace("'", "''") + "'"
        require(
            type(value) in (int, float) and math.isfinite(value),
            "Invalid fixture number",
        )
        return repr(value)

    values = ",".join(
        "(" + ",".join(literal(row[key]) for key in fields) + ")" for row in rows
    )
    expressions = []
    for key in fields:
        kind = (
            "BIGINT" if key == "row_id" else "STRING" if key == "series" else "DOUBLE"
        )
        expressions.append(f"CAST(`{key}` AS {kind}) AS `{key}`")
    return (
        "SELECT "
        + ",".join(expressions)
        + " FROM VALUES "
        + values
        + " AS fixture("
        + ",".join(f"`{key}`" for key in fields)
        + ")"
    )


def descriptor_check(runtime, model_id):
    descriptor = runtime.descriptor(model_id)
    expected_fields = ["x", "y"] if model_id == CORRELATED else ROW_FIELDS[model_id]
    require(descriptor["fit_fields"] == expected_fields, "Prepared fit fields differ")
    require(
        descriptor["fit_kind"] == ("unit" if model_id == CORRELATED else "rows"),
        "Prepared factorization differs",
    )
    require(not descriptor["ordered"], "These fixtures do not assert a temporal order")
    expected_targets = (
        {"existing_group", "new_group"} if model_id == CORRELATED else {"response"}
    )
    for operation in ("predict", "forecast"):
        require(
            set(descriptor[operation]) == expected_targets, "Prepared targets differ"
        )
        for target in expected_targets:
            require(
                descriptor[operation][target]["columns"] == MOMENT_COLUMNS,
                "Prepared moment columns differ",
            )
            require(
                descriptor[operation][target]["fields"] == expected_fields[:-1],
                "Future target needs unexpected fields",
            )
            require(
                descriptor[operation][target]["needs_history"]
                == (target == "existing_group"),
                "Prepared conditioning contract differs",
            )
    return descriptor


def check_output(frame, point, expected, expected_ids, parameter_digest):
    observed = [row.asDict() for row in frame.orderBy("row_id").collect()]
    require(
        [row["row_id"] for row in observed] == expected_ids,
        "Requested row identities differ",
    )
    require(len(observed) == len(expected), "Moment result row count differs")
    for row, target in zip(observed, expected, strict=True):
        for column, value in zip(MOMENT_COLUMNS, target, strict=True):
            close(row["declared_" + column], value)
    metadata = {}
    for column in MOMENT_COLUMNS:
        actual = frame.schema["declared_" + column].metadata
        for key, value in {
            "parameter_set_id": point.document["parameter_set_id"],
            "purpose": "sensitivity",
            "parameter_digest": parameter_digest,
        }.items():
            require(actual.get(key) == value, f"Prediction metadata differs for {key}")
        metadata[column] = actual
    return {"rows": observed, "metadata": metadata}


def run_case(api, spark, model_id, case, reference_sha):
    from ds60_spark_tmbad import (
        ContractError,
        FittedModel,
        ModelSpec,
        PreparedParameters,
    )

    descriptor = descriptor_check(api.runtime, model_id)
    training_rows, future_rows = fixture_rows(model_id, case)
    training = spark.sql(fixture_sql(training_rows)).repartition(2)
    future = spark.sql(fixture_sql(future_rows)).repartition(2)
    groups = ["series"] if model_id == CORRELATED else []
    fields = descriptor["fit_fields"]
    spec = ModelSpec(
        model_id,
        {name: name for name in fields},
        id_columns=["row_id"],
        group_columns=groups,
        weight_column=None if groups else "weight",
    )
    # Reverse the mapping insertion order to verify named coordinate resolution.
    named = dict(
        reversed(
            list(zip(descriptor["parameter_names"], case["parameters"], strict=True))
        )
    )
    evaluation = api.evaluate_shared(training, spec, named)
    require(
        "fit" not in evaluation and "converged" not in evaluation,
        "Evaluation claims a fit",
    )
    require(
        evaluation["row_count"] == len(training_rows), "Evaluation row ledger differs"
    )
    require(
        evaluation["unit_count"] == (1 if groups else 0),
        "Evaluation unit ledger differs",
    )
    require(
        evaluation["weight_sum"] == (1.0 if groups else math.fsum(case["weights"])),
        "Evaluation weight mass differs from the exact fixture weights",
    )
    close(evaluation["loss_components"]["data_sum"], case["value"])
    for actual, expected in zip(
        evaluation["data_gradient_sum"], case["gradient"], strict=True
    ):
        close(actual, expected)
    point = PreparedParameters.from_parameters(
        api.runtime,
        model_id,
        named,
        purpose="sensitivity",
        parameter_set_id=model_id + "-" + case["case"],
        layout={"id_columns": ["row_id"], "group_columns": groups, "order_columns": []},
        provenance={"kind": "sensitivity", "reference_sha256": reference_sha},
    )
    require(
        not {"fit", "converged", "trace"} & point.document.keys(),
        "Parameters claim a fit",
    )
    require(
        PreparedParameters.from_json(point.to_json(), runtime=api.runtime).to_json()
        == point.to_json(),
        "Declared-parameter persistence differs",
    )
    try:
        FittedModel.from_json(point.to_json(), runtime=api.runtime)
    except ContractError:
        pass
    else:
        raise AssertionError("Declared parameters were accepted as a fitted model")
    outputs = []
    for target in descriptor["predict"]:
        conditional = target == "existing_group"
        options = {
            "target": target,
            "columns": {name: name for name in fields[:-1]},
            "output_prefix": "declared_",
        }
        if conditional:
            options["history_columns"] = {name: name for name in fields}
        predicted = point.predict(
            future, history=training if conditional else None, options=options
        )
        expected = moments(case, target)
        expected_ids = [row["row_id"] for row in future_rows]
        prediction = check_output(
            predicted, point, expected, expected_ids, evaluation["parameter_digest"]
        )
        forecast = point.forecast(
            training if conditional else training.limit(0),
            future,
            options={
                "target": target,
                "future_columns": {name: name for name in fields[:-1]},
                "history_columns": {name: name for name in fields}
                if conditional
                else {},
                "output_prefix": "declared_",
            },
        )
        forecast = check_output(
            forecast, point, expected, expected_ids, evaluation["parameter_digest"]
        )
        outputs.append(
            {"target": target, "prediction": prediction, "forecast": forecast}
        )
    return {
        "model_id": model_id,
        "case": case["case"],
        "reference_sha256": reference_sha,
        "parameter_set": point.document,
        "fixed_evaluation": evaluation,
        "targets": outputs,
    }


def check_installed():
    from validate_installed import check_installed as check_installed_wheel

    import ds60_spark_tmbad

    check_installed_wheel()
    distribution = importlib.metadata.distribution("ds60-spark-tmbad")
    actual = Path(ds60_spark_tmbad.__file__).resolve()
    return {
        "version": distribution.version,
        "module_path": str(actual),
        "module_sha256": sha256(actual),
    }


def write_receipt(path, report, *, create=False):
    """Reserve a fresh receipt, then atomically checkpoint only that owned path."""
    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if create:
        with path.open("x") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--row-references", required=True, type=Path)
    parser.add_argument("--gaussian-references", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a fresh evidence output path")
    cases = selected_cases(args.row_references, args.gaussian_references)
    report = {
        "kind": "native-python-new-model-parameter-smoke",
        "status": "running",
        "passed": False,
        "stage": "preflight",
        "manifest_sha256": sha256(args.manifest),
        "validator_sha256": sha256(__file__),
        "reference_sha256": {
            "rows": sha256(args.row_references),
            "gaussian": sha256(args.gaussian_references),
        },
        "tolerances": {"relative": RELATIVE_TOLERANCE, "absolute": ABSOLUTE_TOLERANCE},
        "cases": [],
        "model_count": 9,
        "parameter_data_cases": 0,
        "expected_parameter_data_cases": len(cases),
        "native_execution_attempted": False,
        "native_executed": False,
        "spark_executed": False,
        "optimization_executed": False,
        "hessian_compared": False,
        "posterior_sampling_executed": False,
        "joint_covariance_returned": False,
        "scope": "Fixed values/scores and marginal moments at declared reference parameters; "
        "no independent-fit, optimizer, managed-cloud or multi-container acceptance",
    }
    write_receipt(args.output, report, create=True)
    spark = None
    try:
        report["installed_package"] = check_installed()
        from pyspark.sql import SparkSession

        from ds60_spark_tmbad import PreparedRuntime, SparkTMBad

        runtime = PreparedRuntime.from_manifest(args.manifest)
        require(
            runtime.manifest["package_version"] == "0.2.0",
            "Requires a coherent 0.2.0 artifact",
        )
        for model_id in [*ROW_FIELDS, CORRELATED]:
            descriptor_check(runtime, model_id)
        spark = (
            SparkSession.builder.appName("native-new-model-parameter-smoke")
            .config("spark.driver.maxResultSize", "1m")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )
        report.update(
            spark_version=spark.version,
            master=spark.sparkContext.master,
            stage="native_probe",
            native_execution_attempted=True,
        )
        write_receipt(args.output, report)
        api = SparkTMBad(runtime)
        report.update(
            probe=api.probe(spark, CORRELATED),
            native_executed=True,
            spark_executed=True,
        )
        for model_id, case, reference_sha in cases:
            report.update(
                stage="parameter_case",
                current_case={"model_id": model_id, "case": case["case"]},
            )
            write_receipt(args.output, report)
            report["cases"].append(run_case(api, spark, model_id, case, reference_sha))
            report["parameter_data_cases"] = len(report["cases"])
            write_receipt(args.output, report)
        report["stage"] = "spark_shutdown"
        write_receipt(args.output, report)
        finished_spark, spark = spark, None
        finished_spark.stop()
        report.update(status="passed", passed=True, stage="complete")
        report.pop("current_case", None)
        write_receipt(args.output, report)
        print(
            json.dumps(
                {
                    "passed": True,
                    "model_count": 9,
                    "parameter_data_cases": len(report["cases"]),
                }
            )
        )
    except Exception as error:
        report.update(
            status="failed",
            passed=False,
            error={"type": type(error).__name__, "message": str(error)},
        )
        write_receipt(args.output, report)
        raise
    finally:
        if spark is not None:
            try:
                spark.stop()
            except Exception as cleanup_error:
                report["cleanup_error"] = {
                    "type": type(cleanup_error).__name__,
                    "message": str(cleanup_error),
                }
                write_receipt(args.output, report)
                raise


if __name__ == "__main__":
    main()
