"""Actual installed-wheel/Spark/native checks for the 0.2 target and parameter APIs.

Run explicitly with spark-submit and the matching prepared JAR. This program
does not substitute mock DataFrames or fabricated fit documents for execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

import ds60_spark_tmbad
from ds60_spark_tmbad import (
    ContractError,
    FittedModel,
    ModelSpec,
    PreparedParameters,
    PreparedRuntime,
    SparkTMBad,
)
from pyspark.sql import SparkSession
from validate_installed import check_installed

GALLERY = Path(__file__).parent / "gallery"
sys.path.insert(0, str(GALLERY))
from run_gallery import expected_values, frame  # noqa: E402 - gallery path is set above


def close(actual, expected, tolerance=1e-7):
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"Expected {expected!r}, received {actual!r}")


def normal_target(api, spark, reduction):
    observations = spark.sql(
        "SELECT CAST(id AS BIGINT) AS row_id, CAST(y AS DOUBLE) AS y "
        "FROM VALUES (0,1),(1,2),(2,4),(3,7) AS fixture(id,y)"
    ).repartition(2)
    spec = ModelSpec("normal", {"y": "y"}, id_columns=["row_id"])
    regularization = {
        "schema_version": 1,
        "coordinate_system": "native_optimizer_parameters",
        "normalization": "summed_likelihood_target",
        "gaussian": {"mu": {"mean": 1.0, "precision": 2.0}},
        "l1": {"mu": 1.0},
    }
    target_options = {
        "regularization": regularization,
        "fixed_parameters": {"log_sigma": 0.0},
        "reduction": reduction,
    }
    denominator = 4 if reduction == "weighted_mean" else 1
    fitted = api.fit_shared(
        observations,
        spec,
        options=target_options
        | {
            "initial_parameters": [0.0, 0.0],
            "solver": {
                "method": "proximal_gradient",
                "initial_step": denominator / 6,
                "kkt_tolerance": 1e-7,
            },
            "max_iterations": 100,
        },
    )
    document = fitted.model
    assert document["schema_version"] == 2 and document["fit"]["converged"]
    close(document["parameters"][0], 2.5)
    assert document["parameters"][1] == 0.0
    assert document["target"]["free_parameter_count"] == 1
    assert document["target"]["stationarity"]["summed_inf"] <= 1e-7
    assert document["fit"]["projected_gradient_inf"] > 0.2
    assert not document["fit"]["trace"]
    assert len(document["target"]["proximal_trace"]) == document["fit"]["iterations"]
    evaluated = api.evaluate_shared(
        observations,
        spec,
        {"log_sigma": 0, "mu": document["parameters"][0]},
        options=target_options,
    )
    assert "converged" not in evaluated and evaluated["row_count"] == 4
    assert evaluated["weight_kind"] == "observation"
    close(evaluated["loss_components"]["total_reduced"], document["fit"]["loss"])
    close(evaluated["smooth_gradient_sum"][0], -1)
    assert evaluated["target_spec_digest"] == document["target"]["target_spec_digest"]
    with tempfile.TemporaryDirectory(prefix="tmbad-extended-fit-") as directory:
        path = Path(directory) / "fit.json"
        fitted.save(path)
        loaded = FittedModel.load(path, runtime=api.runtime)
        assert loaded.to_json() == fitted.to_json()
        future = spark.sql("SELECT id + 100 AS row_id FROM range(3)")
        predicted = loaded.predict(future, options={"target": "response", "columns": {}})
        prediction_rows = [row.asDict() for row in predicted.orderBy("row_id").collect()]
        assert len(prediction_rows) == 3
        for row in prediction_rows:
            close(row["tmbad_mean"], 2.5)
            close(row["tmbad_sd"], 1.0)
    try:
        api.evaluate_shared(observations, spec, [2.5, 0.1], options=target_options)
    except ContractError:
        fixed_mismatch_refused = True
    else:
        raise AssertionError("An explicit fixed evaluation point was silently projected")
    all_fixed = api.fit_shared(
        observations,
        spec,
        options={
            "initial_parameters": [0.0, 0.0],
            "fixed_parameters": {"mu": 2.0, "log_sigma": 0.0},
        },
    ).model
    assert all_fixed["fit"]["status"] == "all_parameters_fixed"
    assert all_fixed["fit"]["iterations"] == 0 and all_fixed["fit"]["objective_calls"] == 1
    assert all_fixed["target"]["free_parameter_count"] == 0
    return {
        "reduction": reduction,
        "fit": document,
        "evaluation": evaluated,
        "fitted_predictions": prediction_rows,
        "all_fixed": all_fixed,
        "fixed_point_mismatch_refused_locally": fixed_mismatch_refused,
    }


def declared_ar1(api, spark):
    fixture_path = GALLERY / "fixtures.json"
    recipe = json.loads(fixture_path.read_text())["cases"]["ar1"]
    point = PreparedParameters.from_parameters(
        api.runtime,
        "ar1",
        recipe["generating_parameters"],
        purpose="simulation_truth",
        parameter_set_id="ar1-existing-gallery-generator",
        layout={
            "id_columns": recipe["id_columns"],
            "group_columns": recipe["group_columns"],
            "order_columns": recipe["order_columns"],
        },
        provenance={
            "kind": "simulation_truth",
            "generator_source_sha256": hashlib.sha256(
                (GALLERY / "build_fixtures.py").read_bytes()
            ).hexdigest(),
            "seed": recipe["seed"],
            "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
        },
    )
    assert not {"fit", "converged", "trace"} & point.document.keys()
    conditioning = recipe["forecast_cases"][0]
    history = frame(
        spark, conditioning["history_rows"], list(recipe["training_rows"][0]), ordered=True
    )
    spec = ModelSpec(
        "ar1",
        {name: name for name in recipe["fit_fields"]},
        id_columns=recipe["id_columns"],
        group_columns=recipe["group_columns"],
        order_columns=recipe["order_columns"],
    )
    evaluated = api.evaluate_shared(history, spec, recipe["generating_parameters"])
    assert evaluated["weight_kind"] == "unit" and evaluated["unit_count"] == 1
    prediction_records = []
    for operation in recipe["prediction_cases"]:
        targets = frame(spark, operation["rows"], list(operation["rows"][0]), ordered=True)
        history = frame(
            spark, operation["history_rows"], list(recipe["training_rows"][0]), ordered=True
        )
        options = {
            "target": operation["target"],
            "columns": {name: name for name in operation["fields"]},
            "order_columns": operation["order_columns"],
            "output_prefix": "declared_",
        }
        if operation["history_rows"]:
            options["history_columns"] = {name: name for name in recipe["fit_fields"]}
        output = point.predict(
            targets, history=history if operation["history_rows"] else None, options=options
        )
        actual = [row.asDict() for row in output.orderBy("row_id").collect()]
        expected = expected_values("ar1", recipe["generating_parameters"], operation)
        columns = api.runtime.descriptor("ar1")["predict"][operation["target"]]["columns"]
        assert len(actual) == len(expected) == len(operation["rows"])
        for row, values in zip(actual, expected, strict=True):
            for column, value in zip(columns, values, strict=True):
                close(row["declared_" + column], value, tolerance=1e-8)
        for column in columns:
            assert (
                output.schema["declared_" + column].metadata["parameter_digest"]
                == evaluated["parameter_digest"]
            )
        prediction_records.append({"target": operation["target"], "rows": actual})
    records = []
    for operation in recipe["forecast_cases"]:
        targets = frame(spark, operation["rows"], list(operation["rows"][0]), ordered=True)
        history = frame(
            spark, operation["history_rows"], list(recipe["training_rows"][0]), ordered=True
        )
        output = point.forecast(
            history,
            targets,
            options={
                "target": operation["target"],
                "future_columns": {name: name for name in operation["fields"]},
                "history_columns": {name: name for name in recipe["fit_fields"]},
                "future_order_columns": operation["order_columns"],
                "output_prefix": "declared_",
            },
        )
        actual = [row.asDict() for row in output.orderBy("row_id").collect()]
        expected = expected_values("ar1", recipe["generating_parameters"], operation)
        columns = api.runtime.descriptor("ar1")["forecast"][operation["target"]]["columns"]
        assert len(actual) == len(expected) == 3
        assert [row["row_id"] for row in actual] == [row["row_id"] for row in operation["rows"]]
        for row, values in zip(actual, expected, strict=True):
            for column, value in zip(columns, values, strict=True):
                close(row["declared_" + column], value, tolerance=1e-8)
        for column in columns:
            metadata = output.schema["declared_" + column].metadata
            assert metadata["parameter_set_id"] == point.document["parameter_set_id"]
            assert metadata["purpose"] == "simulation_truth"
            assert metadata["parameter_digest"] == evaluated["parameter_digest"]
        records.append(
            {
                "target": operation["target"],
                "rows": actual,
                "numerical_columns": columns,
                "source_bound_metadata_checked": True,
            }
        )
    with tempfile.TemporaryDirectory(prefix="tmbad-declared-point-") as directory:
        path = Path(directory) / "truth.json"
        point.save(path)
        assert PreparedParameters.load(path, runtime=api.runtime).to_json() == point.to_json()
        try:
            FittedModel.load(path, runtime=api.runtime)
        except ContractError:
            pass
        else:
            raise AssertionError("A declared parameter set was accepted as a converged fit")
    return {
        "parameter_set": point.document,
        "fixed_evaluation": evaluated,
        "prediction_cases": prediction_records,
        "forecast_cases": records,
        "posterior_sampling_executed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a fresh evidence output path")
    check_installed()
    runtime = PreparedRuntime.from_manifest(args.manifest)
    if runtime.manifest["package_version"] != "0.2.0":
        parser.error("This acceptance requires a prepared 0.2.0 artifact")
    spark = (
        SparkSession.builder.appName("native-extended-target-acceptance")
        .config("spark.driver.maxResultSize", "1m")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    try:
        api = SparkTMBad(runtime)
        probe = api.probe(spark, "normal")
        targets = [normal_target(api, spark, reduction) for reduction in ("sum", "weighted_mean")]
        close(targets[0]["fit"]["fit"]["loss"] / 4, targets[1]["fit"]["fit"]["loss"])
        assert (
            targets[0]["fit"]["target"]["target_spec_digest"]
            == targets[1]["fit"]["target"]["target_spec_digest"]
        )
        report = {
            "kind": "installed-native-python-extended-acceptance",
            "package_version": ds60_spark_tmbad.__version__,
            "spark": spark.version,
            "master": spark.sparkContext.master,
            "artifact_identity": runtime.identity("normal"),
            "probe": probe,
            "named_target_cases": targets,
            "declared_parameters": declared_ar1(api, spark),
            "native_executed": True,
            "spark_executed": True,
            "multi_container_qualified_by_this_script": False,
            "posterior_sampler_executed": False,
            "passed": True,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "passed": True,
                    "named_target_cases": 2,
                    "declared_forecast_cases": 2,
                    "source": "actual installed wheel/JVM/native execution",
                }
            )
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
