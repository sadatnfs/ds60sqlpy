# SPDX-License-Identifier: MIT
"""Run one bounded actual native0.2 study shard with visible fit failures."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import time
from pathlib import Path

from extended_support import (
    FIELDS,
    close,
    named_oracle,
    panel_reference,
    penalty_value,
    prediction_metrics,
    require,
    row_moments,
    row_nll,
)
from run_spark import installed, sql_frame
from study_support import canonical, digest

EXPECTED_METHODS = {
    "sim-003": {
        "unpenalized": "linear_gaussian",
        "selected_gaussian": "linear_gaussian",
    },
    "sim-004": {"unpenalized": "linear_gaussian", "selected_l1": "linear_gaussian"},
    "sim-009": {"pooled_shared": "normal", "independent_groups": "normal"},
    "sim-020": {
        "poisson": "poisson_exposure",
        "zero_inflated": "zero_inflated_poisson",
        "hurdle": "hurdle_poisson",
    },
    "sim-022": {"binomial": "binomial_logistic", "beta_binomial": "beta_binomial"},
    "sim-024": {"gaussian": "linear_gaussian", "student_t_df5": "student_t_regression"},
    "sim-028": {
        "known_covariance": "gaussian_correlated_random_slope",
        "estimated_covariance": "gaussian_correlated_random_slope",
    },
}
EXPECTED_SCENARIOS = {
    "sim-003": {"weak_slope", "strong_slope"},
    "sim-004": {"weak_slope", "strong_slope"},
    "sim-009": {"equal_group_means", "heterogeneous_group_means"},
    "sim-020": {"poisson_truth", "structural_zero_truth"},
    "sim-022": {"binomial_truth", "beta_binomial_truth"},
    "sim-024": {"gaussian_truth", "symmetric_contamination"},
    "sim-028": {"positive_correlation", "negative_correlation"},
}


def read_bound(path):
    with path.open("rb") as stream:
        raw = stream.read(4 * 1024 * 1024 + 1)
    require(len(raw) <= 4 * 1024 * 1024, "Study input exceeds 4 MiB")
    document = json.loads(raw)
    require(isinstance(document, dict), "Study input must be a JSON object")
    canonical(document)
    return document, hashlib.sha256(raw).hexdigest()


def admit_methods(cases, study):
    require(
        {case["scenario"] for case in cases} == EXPECTED_SCENARIOS[study],
        "Unexpected scenario selection",
    )
    expected = EXPECTED_METHODS[study]
    for case in cases:
        methods = case["methods"]
        require(
            isinstance(methods, list) and len(methods) == len(expected),
            "Missing or excessive planned methods",
        )
        require(
            len({method["id"] for method in methods}) == len(methods),
            "Duplicate method IDs",
        )
        for method in methods:
            require(
                method["id"] in expected and method["model_id"] == expected[method["id"]],
                "Unexpected model or method",
            )
            allowed = {"id", "model_id", "initial", "fixed", "regularization"}
            if method["id"] == "independent_groups":
                allowed.add("mechanism")
                require(
                    method.get("mechanism") == "independent_groups",
                    "Independent mechanism differs",
                )
            require(set(method) == allowed, "Unexpected method keys or mechanism")
        for split in ("training", "future"):
            require(
                case[split + "_sha256"] == digest(case[split]),
                "Dataset bytes do not match recorded identity",
            )


def metric_schema(case, method):
    cohorts = sorted({row.get("cohort", "future") for row in case["future"]})
    metrics = ["mse", "mean_marginal_nll", "mean_standardized_square"]
    if method["model_id"] in {"normal", "linear_gaussian", "gaussian_correlated_random_slope"}:
        metrics += ["gaussian_pointwise_coverage", "unadjusted_gaussian_bands_path_coverage"]
    return dict.fromkeys(cohorts, metrics)


def checkpoint(path, report):
    body = canonical(report) + b"\n"
    if len(body) > 4 * 1024 * 1024:
        raise ValueError("Study receipt exceeds4MiB")
    temporary = path.with_name(path.name + ".pending")
    with temporary.open("wb") as stream:
        stream.write(body)
    temporary.replace(path)


def fit_options(method, reduction, rows):
    result = {
        "initial_parameters": method["initial"],
        "reduction": reduction,
        "max_iterations": 200,
        "gradient_tolerance": 1e-6,
        "function_tolerance": 0.0,
        "batch_rows": 128,
    }
    if method["fixed"]:
        result["fixed_parameters"] = method["fixed"]
    if method["regularization"] is not None:
        result["regularization"] = method["regularization"]
        if method["regularization"]["l1"]:
            result["solver"] = {
                "method": "proximal_gradient",
                "initial_step": (rows if reduction == "weighted_mean" else 1) / rows,
                "kkt_tolerance": 1e-6,
            }
    return result


def fit_is_qualified(document):
    if not document["fit"]["converged"]:
        return False
    if document["schema_version"] == 2:
        stationarity = document["target"]["stationarity"]
        value = (
            stationarity["summed_inf"]
            if stationarity["tolerance_units"] == "summed_target"
            else stationarity["reduced_inf"]
        )
        return value <= stationarity["tolerance"]
    return document["fit"]["projected_gradient_inf"] <= 1e-6


def predict_fitted(fitted, training, spark, case, method, partitions):
    model = method["model_id"]
    fields = FIELDS[model][:-1]
    result = []
    if model == "gaussian_correlated_random_slope":
        for cohort, target in [("known", "existing_group"), ("unseen", "new_group")]:
            requested = [row for row in case["future"] if row["cohort"] == cohort]
            future = sql_frame(spark, requested, ["row_id", "unit", *fields], partitions)
            prediction = fitted.forecast(
                training if cohort == "known" else training.limit(0),
                future,
                options={
                    "target": target,
                    "future_columns": {n: n for n in fields},
                    "history_columns": {"x": "x", "y": "y"} if cohort == "known" else {},
                },
            )
            result.extend(
                {"row_id": r.row_id, "mean": r.tmbad_mean, "variance": r.tmbad_variance}
                for r in prediction.collect()
            )
    else:
        future = sql_frame(spark, case["future"], ["row_id", *fields], partitions)
        prediction = fitted.predict(
            future, options={"target": "response", "columns": {n: n for n in fields}}
        )
        result = [
            {
                "row_id": r.row_id,
                "mean": r.tmbad_mean,
                "variance": r.tmbad_sd**2 if model == "normal" else r.tmbad_variance,
            }
            for r in prediction.collect()
        ]
    return result


def shared_record(api, spark, case, method, reduction, partitions):
    from ds60_spark_tmbad import ModelSpec

    model = method["model_id"]
    panel = model == "gaussian_correlated_random_slope"
    columns = ["row_id", *FIELDS[model], *(["unit"] if panel else [])]
    training = sql_frame(spark, case["training"], columns, partitions)
    spec = ModelSpec(
        model,
        {name: name for name in FIELDS[model]},
        id_columns=["row_id"],
        group_columns=["unit"] if panel else [],
    )
    fitted = api.fit_shared(
        training, spec, options=fit_options(method, reduction, len(case["training"]))
    )
    document = fitted.model
    theta = document["parameters"]
    descriptor = api.runtime.descriptor(model)
    evaluation_options = {
        k: v
        for k, v in fit_options(method, reduction, len(case["training"])).items()
        if k in {"reduction", "regularization", "fixed_parameters", "batch_rows"}
    }
    evaluated = api.evaluate_shared(training, spec, theta, options=evaluation_options)
    reference_data = (
        panel_reference(theta, case["training"], [])[0]
        if panel
        else math.fsum(row_nll(model, theta, row) for row in case["training"])
    )
    close(evaluated["loss_components"]["data_sum"], reference_data)
    penalty = penalty_value(theta, descriptor["parameter_names"], method["regularization"])
    denominator = (
        (len({row["unit"] for row in case["training"]}) if panel else len(case["training"]))
        if reduction == "weighted_mean"
        else 1
    )
    close(document["fit"]["loss"], (reference_data + penalty) / denominator)
    require(
        evaluated["row_count"] == len(case["training"]),
        "Actual training row coverage differs",
    )
    record = {
        "status": "passed" if fit_is_qualified(document) else "failed",
        "parameters": theta,
        "fit": document["fit"],
        "target": document.get("target"),
        "fixed_evaluation": evaluated,
        "reference_data_sum": reference_data,
        "reference_penalty_sum": penalty,
        "model_descriptor_digest": descriptor["digest"],
        ("prediction_scope"): (
            "Actual native response-free moments; plug-in fitted population parameters"
        ),
    }
    if record["status"] == "failed":
        record["failure_category"] = "optimizer_not_certified_by_declared_stationarity"
        return record
    if case["study"] in {"sim-003", "sim-004"}:
        oracle = named_oracle(case, method)
        for actual, expected in zip(theta, oracle["parameters"], strict=True):
            close(actual, expected, absolute=2e-6)
        close(document["fit"]["loss"], oracle["summed_target"] / denominator)
        record["analytic_target_oracle"] = oracle
    predictions = predict_fitted(fitted, training, spark, case, method, partitions)
    expected = (
        panel_reference(theta, case["training"], case["future"])[1]
        if panel
        else [
            {
                "row_id": row["row_id"],
                "mean": row_moments(model, theta, row)[0],
                "variance": row_moments(model, theta, row)[1],
            }
            for row in case["future"]
        ]
    )
    index = {p["row_id"]: p for p in predictions}
    require(
        len(index) == len(predictions) == len(expected),
        "Prediction identity count differs",
    )
    for item in expected:
        for field in ["mean", "variance"]:
            close(index[item["row_id"]][field], item[field])
    record["future_metrics"] = prediction_metrics(case, model, theta, predictions)
    record["prediction_sha256"] = digest(sorted(predictions, key=lambda p: p["row_id"]))
    record["future_rows"] = len(predictions)
    truth = case["truth"]
    if truth["model_id"] == model and truth.get("parameters") is not None:
        record["parameter_errors"] = [
            observed - reference
            for name, observed, reference in zip(
                descriptor["parameter_names"], theta, truth["parameters"], strict=True
            )
            if name not in method["fixed"]
        ]
        record["parameter_error_names"] = [
            name for name in descriptor["parameter_names"] if name not in method["fixed"]
        ]
    else:
        record["parameter_error_scope"] = (
            "No correct-family finite truth vector is asserted for this fitted model"
        )
    return record


def independent_record(api, spark, case, method, partitions):
    from ds60_spark_tmbad import ModelSpec
    from pyspark.sql import functions as F

    training = sql_frame(spark, case["training"], ["row_id", "unit", "y"], partitions)
    grouped = api.fit_groups(
        training,
        ModelSpec("normal", {"y": "y"}, id_columns=["row_id"], group_columns=["unit"]),
        options=fit_options(method, "sum", len(case["training"])),
    )
    models = grouped.models.persist()
    try:
        summary = (
            models.agg(
                F.count("*").alias("groups"),
                F.sum(F.col("tmbad_converged").cast("long")).alias("successful_groups"),
                F.sum("tmbad_row_count").alias("training_rows"),
                F.max("tmbad_projected_gradient_inf").alias("maximum_projected_score"),
            )
            .first()
            .asDict()
        )
        expected_groups = len({row["unit"] for row in case["training"]})
        require(
            summary["groups"] == expected_groups
            and summary["training_rows"] == len(case["training"]),
            "Independent group coverage differs",
        )
        # A complete failed fit is retained; no fitted model JSON is collected.
        if summary["successful_groups"] != expected_groups:
            return {
                "status": "failed",
                "failure_category": "one_or_more_independent_groups_unconverged",
                "group_summary": summary,
                "model_documents_collected": False,
            }
        require(summary["maximum_projected_score"] <= 1e-6, "Independent score gate differs")
        future = sql_frame(spark, case["future"], ["row_id", "unit"], partitions)
        output = api.from_group_models(models).predict(
            future, options={"target": "response", "columns": {}}
        )
        predictions = [
            {"row_id": r.row_id, "mean": r.tmbad_mean, "variance": r.tmbad_sd**2}
            for r in output.collect()
        ]
        # Reference calculations use the original tiny generated fixtures.
        # Spark observations are not collected for these calculations.
        oracle = {}
        for unit in case["truth"]["group_parameters"]:
            values = [row["y"] for row in case["training"] if row["unit"] == unit]
            center = math.fsum(values) / len(values)
            variance = math.fsum((x - center) ** 2 for x in values) / len(values)
            oracle[unit] = (center, variance)
        index = {p["row_id"]: p for p in predictions}
        require(
            len(index) == len(case["future"]),
            "Independent future row identities differ",
        )
        for row in case["future"]:
            location, variance = oracle[row["unit"]]
            close(index[row["row_id"]]["mean"], location, absolute=2e-6)
            close(index[row["row_id"]]["variance"], variance, absolute=2e-6)
        return {
            "status": "passed",
            "group_summary": summary,
            "model_documents_collected": False,
            "future_metrics": prediction_metrics(case, "normal", None, predictions),
            "future_rows": len(predictions),
            "prediction_sha256": digest(sorted(predictions, key=lambda p: p["row_id"])),
            ("prediction_scope"): (
                "Actual independent-group fits and response-free conditional Gaussian "
                "observations; no shared random-effect integration"
            ),
        }
    finally:
        models.unpersist()


def truth_record(api, spark, case, bundle, fixture_sha256, partitions):
    """Exercise declared truth parameters without constructing a fitted document."""
    from ds60_spark_tmbad import PreparedParameters

    truth = case["truth"]
    if truth.get("model_id") is None or truth.get("parameters") is None:
        return {
            "status": "not_applicable",
            "reason": "No single correctly specified finite population vector for this scenario",
        }
    model = truth["model_id"]
    panel = model == "gaussian_correlated_random_slope"
    point = PreparedParameters.from_parameters(
        api.runtime,
        model,
        truth["parameters"],
        purpose="simulation_truth",
        parameter_set_id=case["study"] + "-" + case["scenario"] + "-r" + str(case["replicate"]),
        layout={
            "id_columns": ["row_id"],
            "group_columns": ["unit"] if panel else [],
            "order_columns": [],
        },
        provenance={
            "kind": "simulation_truth",
            "generator_source_sha256": bundle["generator_sha256"],
            "seed": bundle["seed"],
            "fixture_sha256": fixture_sha256,
        },
    )
    training = sql_frame(
        spark,
        case["training"],
        ["row_id", *FIELDS[model], *(["unit"] if panel else [])],
        partitions,
    )
    predictions = predict_fitted(point, training, spark, case, {"model_id": model}, partitions)
    expected = (
        panel_reference(truth["parameters"], case["training"], case["future"])[1]
        if panel
        else [
            {
                "row_id": row["row_id"],
                "mean": row_moments(model, truth["parameters"], row)[0],
                "variance": row_moments(model, truth["parameters"], row)[1],
            }
            for row in case["future"]
        ]
    )
    index = {row["row_id"]: row for row in predictions}
    require(
        len(index) == len(predictions) == len(expected),
        "Truth prediction identity count differs",
    )
    for row in expected:
        for field in ["mean", "variance"]:
            close(index[row["row_id"]][field], row[field])
    require(
        not {"fit", "converged"} & point.document.keys(),
        "Truth parameters must not claim fitting",
    )
    return {
        "status": "passed",
        "parameter_document": point.document,
        "future_metrics": prediction_metrics(case, model, truth["parameters"], predictions),
        "prediction_sha256": digest(sorted(predictions, key=lambda row: row["row_id"])),
        ("scope"): (
            "Actual declared-truth native moments; generating population parameters treated "
            "as known, no posterior inference"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=Path(__file__).with_name("fixtures") / "native020-smoke.json",
    )
    parser.add_argument(
        "--study",
        required=True,
        choices=[
            "sim-003",
            "sim-004",
            "sim-009",
            "sim-020",
            "sim-022",
            "sim-024",
            "sim-028",
        ],
    )
    parser.add_argument("--replicate", type=int, default=0)
    parser.add_argument("--partitions", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a fresh study output path")
    require(1 <= args.partitions <= 8 and args.replicate >= 0, "Invalid study bounds")
    bundle, fixture_sha256 = read_bound(args.fixtures)
    require(
        bundle["generator_sha256"]
        == hashlib.sha256(
            Path(__file__).with_name("generate_extended_fixtures.py").read_bytes()
        ).hexdigest(),
        "Fixture generator differs from current retained source",
    )
    require(
        bundle.get("schema_version") == 1 and bundle["kind"] == "native020-study-fixtures",
        "Wrong fixture schema or kind",
    )
    require(
        type(bundle["seed"]) is int and 0 <= bundle["seed"] < 2**53,
        "Fixture seed is outside the exact provenance range",
    )
    cases = [
        c for c in bundle["cases"] if c["study"] == args.study and c["replicate"] == args.replicate
    ]
    require(
        len(cases) == 2 and len({c["scenario"] for c in cases}) == 2,
        "Expected exactly two changed scenarios",
    )
    admit_methods(cases, args.study)
    for case in cases:
        require(
            1 <= len(case["training"]) <= 4096 and 1 <= len(case["future"]) <= 128,
            "Study row bounds exceeded",
        )
        training_ids = {r["row_id"] for r in case["training"]}
        future_ids = {r["row_id"] for r in case["future"]}
        require(
            len(training_ids) == len(case["training"])
            and len(future_ids) == len(case["future"])
            and not training_ids & future_ids,
            "Train/future identities overlap",
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        stream.write("{}\n")
    reductions = ["sum", "weighted_mean"] if args.study in {"sim-003", "sim-004"} else ["sum"]
    planned = [
        {
            "scenario": c["scenario"],
            "method": m["id"],
            "reduction": r,
            "case_sha256": digest(c),
        }
        for c in cases
        for m in c["methods"]
        for r in reductions
    ]
    report = {
        "schema_version": 1,
        "kind": "native020-actual-study",
        "status": "running",
        "study": args.study,
        "replicate": args.replicate,
        "seed": bundle["seed"],
        "fixture_sha256": fixture_sha256,
        "dataset_identities": {
            case["scenario"]: {
                split + "_sha256": case[split + "_sha256"] for split in ("training", "future")
            }
            for case in cases
        },
        "generator_sha256": bundle["generator_sha256"],
        "partitions": args.partitions,
        "planned_records": planned,
        "records": [],
        "source_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in [
                "run_native_extended.py",
                "generate_extended_fixtures.py",
                "extended_support.py",
                "study_support.py",
                "run_spark.py",
            ]
        },
        ("scope"): (
            "One bounded actual Spark/native shard. Failed fits remain visible. Repetitions "
            "are independent generated datasets; smoke is not scientific calibration or "
            "distributed-scale acceptance."
        ),
    }
    checkpoint(args.output, report)
    spark = None
    failure = None
    start = time.monotonic()
    try:
        report["package_identity"] = installed("ds60_spark_tmbad", "ds60-spark-tmbad")
        from ds60_spark_tmbad import PreparedRuntime, SparkTMBad
        from pyspark.sql import SparkSession

        manifest_document, manifest_sha256 = read_bound(args.manifest)
        runtime = PreparedRuntime(manifest_document)
        runtime.verify_files()
        require(
            runtime.manifest["package_version"] == "0.2.0",
            "Requires coherent native0.2 artifact",
        )
        report["artifact_identity"] = {
            "manifest_sha256": manifest_sha256,
            "build_id": runtime.manifest["build_id"],
            "binary": runtime.manifest["binary"],
            "jvm": runtime.manifest["jvm"],
            "engine": runtime.manifest["engine"],
        }
        spark = (
            SparkSession.builder.appName("Native0.2 explicit modeling study")
            .config("spark.driver.maxResultSize", "1m")
            .config("spark.sql.shuffle.partitions", str(args.partitions))
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("WARN")
        api = SparkTMBad(runtime)
        report["environment"] = {
            "spark": spark.version,
            "master": spark.sparkContext.master,
            "python": platform.python_version(),
            "machine": platform.machine(),
            "java": spark._jvm.java.lang.System.getProperty("java.version"),
        }
        report["probe"] = api.probe(spark, "normal")
        require(report["probe"]["passed"], "Native preflight failed")
        report["truth_predictions"] = []
        for case in cases:
            report["truth_predictions"].append(
                {
                    "scenario": case["scenario"],
                    **truth_record(
                        api,
                        spark,
                        case,
                        bundle,
                        report["fixture_sha256"],
                        args.partitions,
                    ),
                }
            )
            checkpoint(args.output, report)
            for method in case["methods"]:
                for reduction in reductions:
                    record = {
                        "scenario": case["scenario"],
                        "method": method["id"],
                        "reduction": reduction,
                        "case_sha256": digest(case),
                        "target_configuration": method,
                        "metric_schema": metric_schema(case, method),
                        "truth": case["truth"],
                        "status": "running",
                        "training_rows": len(case["training"]),
                        "future_rows": len(case["future"]),
                    }
                    report["records"].append(record)
                    checkpoint(args.output, report)
                    before = time.monotonic()
                    result = (
                        independent_record(api, spark, case, method, args.partitions)
                        if method.get("mechanism") == "independent_groups"
                        else shared_record(api, spark, case, method, reduction, args.partitions)
                    )
                    record.update(result)
                    record["elapsed_seconds"] = time.monotonic() - before
                    checkpoint(args.output, report)
        if len(reductions) == 2:
            for case in cases:
                for method in case["methods"]:
                    records = [
                        r
                        for r in report["records"]
                        if r["scenario"] == case["scenario"] and r["method"] == method["id"]
                    ]
                    if all(r["status"] == "passed" for r in records):
                        for a, b in zip(
                            records[0]["parameters"],
                            records[1]["parameters"],
                            strict=True,
                        ):
                            close(a, b, absolute=2e-6)
        require(
            installed("ds60_spark_tmbad", "ds60-spark-tmbad") == report["package_identity"],
            "Installed source changed during study",
        )
        runtime.verify_files()
        report["status"] = "completed"
    except Exception as error:  # noqa: BLE001 - checkpoint and re-raise every interrupted shard.
        report["status"] = "interrupted"
        report["error"] = {"type": type(error).__name__, "message": str(error)[:4000]}
        failure = error
    finally:
        if spark is not None:
            try:
                spark.stop()
            except Exception as error:  # noqa: BLE001 - failed shutdown cannot count as completion.
                report["status"] = "interrupted"
                report["shutdown_error"] = repr(error)
                failure = failure or error
        report["elapsed_seconds"] = time.monotonic() - start
        checkpoint(args.output, report)
    if failure is not None:
        raise failure
    print(
        json.dumps(
            {
                "status": report["status"],
                "records": len(report["records"]),
                "failed_fits": sum(r["status"] == "failed" for r in report["records"]),
            }
        )
    )


if __name__ == "__main__":
    main()
