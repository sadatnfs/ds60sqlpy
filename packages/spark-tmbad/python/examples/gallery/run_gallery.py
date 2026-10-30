"""Run real Spark fits and response-free predictions/forecasts for gallery models."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from numerical_oracles import (  # noqa: E402
    ar1_forecast,
    gaussian_ar1_random_intercept_prediction,
    gaussian_random_intercept_prediction,
    poisson_random_intercept_prediction,
    poisson_random_slope_prediction,
)


def expected_values(model_id, theta, operation):
    rows, history = operation["rows"], operation["history_rows"]
    if model_id.startswith("gaussian_random_intercept"):
        value = gaussian_random_intercept_prediction(
            theta, [row["y"] for row in history] if history else None
        )
        return [value for _ in rows]
    if model_id == "poisson_random_intercept":
        observed = [[row["exposure"], row["y"]] for row in history] or None
        return [
            poisson_random_intercept_prediction(theta, row["exposure"], observed) for row in rows
        ]
    if model_id == "poisson_random_slope":
        observed = [[row["x"], row["exposure"], row["y"]] for row in history] or None
        return [
            poisson_random_slope_prediction(theta, row["x"], row["exposure"], observed)
            for row in rows
        ]
    if model_id == "gaussian_ar1_random_intercept":
        return gaussian_ar1_random_intercept_prediction(
            theta,
            [row["time"] for row in rows],
            [[row["time"], row["y"]] for row in history] or None,
        )
    if model_id == "ar1":
        if operation["target"] == "response":
            return [ar1_forecast(theta, [1], row["lag"])[0] for row in rows]
        return ar1_forecast(
            theta, list(range(1, len(rows) + 1)), history[-1]["y"] if history else None
        )
    result = []
    for row in rows:
        if model_id == "normal":
            result.append([theta[0], math.exp(theta[1])])
            continue
        if model_id in ("linear_gaussian", "quadratic_gaussian"):
            design = row["x"] if model_id == "linear_gaussian" else row["x"] ** 2
            mean, variance = theta[0] + theta[1] * design, math.exp(2 * theta[2])
        elif model_id == "saturating_growth":
            mean = theta[0] + math.exp(theta[1]) * (-math.expm1(-math.exp(theta[2]) * row["time"]))
            variance = math.exp(2 * theta[3])
        elif model_id == "bernoulli_logistic":
            eta = theta[0] + theta[1] * row["x"]
            tail = math.exp(-abs(eta))
            mean = 1 / (1 + tail) if eta >= 0 else tail / (1 + tail)
            variance = tail / (1 + tail) ** 2
        else:
            mean = math.exp(theta[0] + theta[1] * row["x"]) * row.get("exposure", 1.0)
            variance = mean if model_id == "poisson_exposure" else mean * mean / math.exp(theta[2])
            if model_id == "negative_binomial2":
                variance += mean
        result.append([mean, variance, math.sqrt(variance)])
    return result


def frame(spark, rows, columns, *, ordered=False):
    """Small SQL VALUES fixtures execute entirely through JVM Spark operators."""

    def quoted(name):
        return "`" + name.replace("`", "``") + "`"

    def data_type(name):
        if name == "series":
            return "STRING"
        return "BIGINT" if name == "row_id" or (ordered and name == "time") else "DOUBLE"

    def literal(value):
        if isinstance(value, str):
            return "'" + value.replace("'", "''") + "'"
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError("Fixture values must be finite numbers or strings")
        return repr(value)

    if not rows:
        projection = ",".join(
            f"CAST(NULL AS {data_type(name)}) AS {quoted(name)}" for name in columns
        )
        return spark.sql("SELECT " + projection + " WHERE FALSE")
    projection = ",".join(
        f"CAST({quoted(name)} AS {data_type(name)}) AS {quoted(name)}" for name in columns
    )
    values = ",".join("(" + ",".join(literal(row[name]) for name in columns) + ")" for row in rows)
    return spark.sql(
        "SELECT "
        + projection
        + " FROM VALUES "
        + values
        + " AS fixture("
        + ",".join(map(quoted, columns))
        + ")"
    )


def verify_operation(api, fitted, spark, recipe, operation, forecast):
    ordered = bool(recipe["order_columns"])
    targets = frame(spark, operation["rows"], list(operation["rows"][0]), ordered=ordered)
    history_rows = operation["history_rows"]
    history = frame(spark, history_rows, list(recipe["training_rows"][0]), ordered=ordered)
    mapping = {name: name for name in operation["fields"]}
    options = {"target": operation["target"], "output_prefix": "example_"}
    if forecast:
        options.update(
            history_columns={name: name for name in recipe["fit_fields"]},
            future_columns=mapping,
            future_order_columns=operation["order_columns"],
        )
        output = fitted.forecast(history, targets, options=options)
        target = api.runtime.descriptor(recipe["model_id"])["forecast"][operation["target"]]
    else:
        options.update(columns=mapping, order_columns=operation["order_columns"])
        if history_rows:
            options["history_columns"] = {name: name for name in recipe["fit_fields"]}
        output = fitted.predict(targets, history=history if history_rows else None, options=options)
        target = api.runtime.descriptor(recipe["model_id"])["predict"][operation["target"]]
    actual = [row.asDict() for row in output.orderBy("row_id").collect()]
    reference = expected_values(recipe["model_id"], fitted.model["parameters"], operation)
    if [row["row_id"] for row in actual] != [row["row_id"] for row in operation["rows"]]:
        raise AssertionError("Prediction/forecast lost or duplicated a requested row identity")
    for row, expected in zip(actual, reference, strict=True):
        if len(target["columns"]) != len(expected):
            raise AssertionError(
                "Declared output columns differ from the independent target formula"
            )
        for name, value in zip(target["columns"], expected, strict=True):
            if not math.isclose(row["example_" + name], value, rel_tol=3e-6, abs_tol=3e-6):
                raise AssertionError(
                    f"{recipe['model_id']} {operation['target']} disagrees with "
                    f"independent {name} formula"
                )
    return {
        "operation": "forecast" if forecast else "predict",
        "target": operation["target"],
        "rows": actual,
        "conditioning": target["conditioning"],
        "uncertainty": target["uncertainty"],
        "formula_check": "passed",
        "response_column_supplied": False,
    }


def run_model(api, spark, recipe, output_directory):
    from ds60_spark_tmbad import FittedModel, ModelSpec

    model_id = recipe["model_id"]
    descriptor = api.describe(spark, model_id)
    if descriptor["fit_fields"] != recipe["fit_fields"]:
        raise AssertionError("Gallery field order differs from the prepared native descriptor")
    training = frame(
        spark,
        recipe["training_rows"],
        list(recipe["training_rows"][0]),
        ordered=bool(recipe["order_columns"]),
    )
    spec = ModelSpec(
        model_id,
        {name: name for name in recipe["fit_fields"]},
        id_columns=recipe["id_columns"],
        group_columns=recipe["group_columns"],
        order_columns=recipe["order_columns"],
    )
    fitted = api.fit_shared(
        training.repartition(2),
        spec,
        options={**recipe["fit_options"], "initial_parameters": recipe["initial_parameters"]},
    )
    model_path = output_directory / f"{model_id}.json"
    fitted.save(model_path)
    restored = FittedModel.load(model_path, runtime=api.runtime)
    if restored.to_json() != fitted.to_json():
        raise AssertionError("Saved model changed during the source-bound JSON round trip")
    record = {
        "model_id": model_id,
        "model_digest": descriptor["digest"],
        "parameter_names": descriptor["parameter_names"],
        "generating_parameters": recipe["generating_parameters"],
        "fitted_parameters": fitted.model["parameters"],
        "fit": fitted.model["fit"],
        "status": "failed",
        "json_round_trip": "passed",
        "operations": [],
    }
    if not fitted.model["fit"]["converged"]:
        record["reason"] = "Fit did not converge; predictions and forecasts were withheld"
        return record
    for forecast, operations in (
        (False, recipe["prediction_cases"]),
        (True, recipe["forecast_cases"]),
    ):
        for operation in operations:
            record["operations"].append(
                verify_operation(api, restored, spark, recipe, operation, forecast)
            )
    record["status"] = "passed"
    return record


def main_for(model_id=None):
    import importlib.metadata

    import ds60_spark_tmbad
    from ds60_spark_tmbad import PreparedRuntime, SparkTMBad
    from pyspark.sql import SparkSession

    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    if model_id is None:
        parser.add_argument("--model", default="all")
    parser.add_argument(
        "--output", type=Path, help="Fresh owned directory for JSON models and report"
    )
    args = parser.parse_args()
    distribution = importlib.metadata.distribution("ds60-spark-tmbad")
    installed = Path(distribution.locate_file("ds60_spark_tmbad/__init__.py")).resolve()
    if installed != Path(ds60_spark_tmbad.__file__).resolve():
        raise RuntimeError("Run the gallery against the non-editable installed Python wheel")
    selected = model_id if model_id is not None else args.model
    fixture_path = Path(__file__).with_name("fixtures.json")
    fixtures = json.loads(fixture_path.read_text())["cases"]
    runtime = PreparedRuntime.from_manifest(args.manifest)
    if selected == "all" and set(fixtures) != set(runtime.model_ids):
        raise ValueError("The full gallery and prepared registry have different model sets")
    names = sorted(fixtures) if selected == "all" else [selected]
    for name in names:
        if name not in fixtures or name not in runtime.model_ids:
            raise ValueError(f"No prepared gallery example for {name}")
    temporary = (
        tempfile.TemporaryDirectory(prefix="spark-tmbad-gallery-") if args.output is None else None
    )
    destination = Path(temporary.name) if temporary else args.output
    if not temporary:
        destination.mkdir(parents=True, exist_ok=False)
    spark = (
        SparkSession.builder.appName("Spark TMBad model gallery")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    results = []
    try:
        api = SparkTMBad(runtime)
        for name in names:
            try:
                results.append(run_model(api, spark, fixtures[name], destination))
            except Exception as error:
                results.append(
                    {
                        "model_id": name,
                        "status": "failed",
                        "error_type": type(error).__name__,
                        "error": str(error)[:1500],
                    }
                )
        report = {
            "schema_version": 1,
            "kind": "spark-tmbad-gallery-execution",
            "status": "passed" if all(row["status"] == "passed" for row in results) else "failed",
            "scope": (
                "actual Spark DataFrame fit, prediction and forecast; observed deployment only"
            ),
            "spark_version": spark.version,
            "platform": runtime.manifest["platform"],
            "artifact_build_id": runtime.manifest["build_id"],
            "artifact_identity": runtime.identity(names[0]),
            "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python_distribution_version": distribution.version,
            "python_source_sha256": {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(installed.parent.glob("*.py"))
            },
            "models": results,
        }
        text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
        (destination / "gallery-report.json").write_text(text + "\n")
        print(text)
        if report["status"] != "passed":
            raise SystemExit(1)
    finally:
        spark.stop()
        if temporary:
            temporary.cleanup()


if __name__ == "__main__":
    main_for()
