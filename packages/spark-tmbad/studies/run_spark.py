"""Run one bounded study shard through an explicitly prepared installed Spark backend.

No package is installed, compiled or downloaded here. Native runs additionally
need the matching JAR on spark-submit --jars and a prepared artifact manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import math
import platform
import re
import time
from pathlib import Path
from typing import Any

from study_support import (
    canonical,
    digest,
    forecast_metrics,
    objective,
    prediction_reference,
)


def installed(package: str, distribution: str) -> dict[str, Any]:
    module = importlib.import_module(package)
    dist = importlib.metadata.distribution(distribution)
    expected = Path(dist.locate_file(package + "/__init__.py")).resolve()
    if Path(module.__file__).resolve() != expected or dist.read_text("WHEEL") is None:
        raise RuntimeError("Qualified studies require the installed wheel, not a source shadow")
    direct = dist.read_text("direct_url.json")
    if direct and json.loads(direct).get("dir_info", {}).get("editable", False):
        raise RuntimeError("Qualified studies require a non-editable wheel")
    files = {
        str(item): hashlib.sha256(Path(dist.locate_file(item)).read_bytes()).hexdigest()
        for item in dist.files or ()
        if str(item).startswith(package + "/") and str(item).endswith(".py")
    }
    return {"distribution": distribution, "version": dist.version, "module_sha256": files}


def sql_frame(spark: Any, rows: list[dict[str, Any]], columns: list[str], partitions: int) -> Any:
    if not rows or len(rows) > 4096 or not 1 <= partitions <= 8:
        raise ValueError("Study SQL fixtures require 1..4096 rows and 1..8 partitions")
    if len(columns) != len(set(columns)) or not all(
        re.fullmatch(r"[a-z][a-z0-9_]*", name) for name in columns
    ):
        raise ValueError("Study fixture column names must be fixed simple identifiers")

    def literal(value: Any) -> str:
        if type(value) is int and abs(value) < 2**53:
            return f"CAST({value} AS BIGINT)"
        if type(value) is float and math.isfinite(value):
            return f"CAST({value!r} AS DOUBLE)"
        if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_]+", value):
            return "'" + value + "'"
        raise ValueError("Unexpected study SQL value or lossy integer")

    values = ",".join("(" + ",".join(literal(row[name]) for name in columns) + ")" for row in rows)
    return spark.sql(
        "SELECT * FROM VALUES " + values + " AS fixture(" + ",".join(columns) + ")"
    ).repartition(partitions)


def bounds(case: str) -> list[tuple[float | None, float | None]]:
    return {
        "normal_mle": [(None, None), (-20.0, 20.0)],
        "linear_all_coordinate_map": [(None, None), (None, None), (-20.0, 20.0)],
        "nonlinear_growth": [(None, None), (-12.0, 12.0), (-12.0, 5.0), (-20.0, 20.0)],
        "random_intercept": [(None, None), (-20.0, 20.0), (-20.0, 20.0)],
    }[case]


def projected_score(theta: list[float], gradient: list[float], case: str) -> float:
    selected = []
    for value, g, (low, high) in zip(theta, gradient, bounds(case), strict=True):
        selected.append(
            0.0
            if (
                (low is not None and value == low and g > 0)
                or (high is not None and value == high and g < 0)
            )
            else g
        )
    return max(abs(x) for x in selected)


def native_fit(
    spark: Any, api: Any, case: dict[str, Any], strength: float, partitions: int
) -> dict[str, Any]:
    from ds60_spark_tmbad import ModelSpec

    kind = case["case"]
    native_id = {
        "normal_mle": "normal",
        "linear_all_coordinate_map": "linear_gaussian",
        "nonlinear_growth": "saturating_growth",
        "random_intercept": "gaussian_random_intercept",
    }[kind]
    fields = {
        "normal_mle": ["y"],
        "linear_all_coordinate_map": ["x", "y"],
        "nonlinear_growth": ["time", "y"],
        "random_intercept": ["y"],
    }[kind]
    training_columns = ["row_id"] + fields + (["unit"] if kind == "random_intercept" else [])
    weighted = kind == "normal_mle"
    if weighted:
        training_columns.append("weight")
    training = sql_frame(spark, case["training"], training_columns, partitions)
    specification = ModelSpec(
        native_id,
        {x: x for x in fields},
        id_columns=["row_id"],
        group_columns=["unit"] if kind == "random_intercept" else [],
        weight_column="weight" if weighted else None,
    )
    fitted = api.fit_shared(
        training,
        specification,
        options={
            "initial_parameters": case["initial"],
            "reduction": "sum",
            "l2_strength": strength,
            "max_iterations": 300,
            "gradient_tolerance": 1e-5,
            "function_tolerance": 0.0,
            "batch_rows": 64,
        },
    )
    document = fitted.model
    theta = document["parameters"]
    diagnostics = document["fit"]
    result = {
        "parameters": theta,
        "observed_objective": diagnostics["loss"],
        "diagnostics": diagnostics,
        "model_descriptor": api.runtime.descriptor(native_id),
        "predictions": [],
    }
    if not diagnostics["converged"]:
        return result
    if kind == "random_intercept":
        for cohort, target in [("known", "existing_group"), ("unseen", "new_group")]:
            rows = [row for row in case["future"] if row["cohort"] == cohort]
            future = sql_frame(spark, rows, ["row_id", "unit"], partitions)
            history = training if cohort == "known" else training.limit(0)
            output = fitted.forecast(
                history,
                future,
                options={"target": target, "future_columns": {}, "history_columns": {"y": "y"}},
            ).collect()
            result["predictions"].extend(
                {
                    "row_id": row.row_id,
                    "mean": row.tmbad_mean,
                    "variance": row.tmbad_variance,
                    "cohort": cohort,
                }
                for row in output
            )
        result["prediction_scope"] = (
            "Actual native known/new-group pointwise forecasts; fixed population parameters"
        )
    else:
        features = (
            []
            if kind == "normal_mle"
            else ["x"]
            if kind == "linear_all_coordinate_map"
            else ["time"]
        )
        future = sql_frame(spark, case["future"], ["row_id"] + features, partitions)
        output = fitted.predict(
            future, options={"target": "response", "columns": {x: x for x in features}}
        ).collect()
        result["predictions"] = [
            {
                "row_id": row.row_id,
                "mean": row.tmbad_mean,
                "variance": row.tmbad_sd**2 if kind == "normal_mle" else row.tmbad_variance,
                "cohort": "future",
            }
            for row in output
        ]
        result["prediction_scope"] = (
            "Actual native response-free prediction; plug-in observation moments"
        )
    return result


def torch_fit(spark: Any, case: dict[str, Any], strength: float, partitions: int) -> dict[str, Any]:
    from ds60_spark_likelihood.dataframe import DataFrameObjective, predict_dataframe
    from ds60_spark_likelihood.optimization import minimize_lbfgsb

    kind = case["case"]
    model = {
        "normal_mle": "normal_mean",
        "linear_all_coordinate_map": "linear_gaussian",
        "nonlinear_growth": "nonlinear_gaussian",
        "random_intercept": "gaussian_random_intercept",
    }[kind]
    features = {
        "normal_mle": {},
        "linear_all_coordinate_map": {"x0": "one", "x1": "x"},
        "nonlinear_growth": {"time": "time"},
        "random_intercept": {},
    }[kind]
    configuration = {"feature_count": 2} if kind == "linear_all_coordinate_map" else None
    weighted = kind == "normal_mle"
    columns = (
        ["row_id"]
        + list(features.values())
        + ["y"]
        + (["weight"] if weighted else [])
        + (["unit"] if kind == "random_intercept" else [])
    )
    frame = sql_frame(spark, case["training"], columns, partitions)
    initial = list(case["initial"])
    limits = bounds(kind)
    if kind == "nonlinear_growth":
        if strength:
            raise ValueError(
                "The native/Torch nonlinear coordinate map does not preserve isotropic L2"
            )
        b, a, r, s = initial
        amplitude = math.exp(a)
        initial = [-amplitude, r, b + amplitude, s]
        limits = [(-math.exp(12), -math.exp(-12)), (-12.0, 5.0), (None, None), (-20.0, 20.0)]
    with DataFrameObjective(
        frame,
        model,
        feature_columns=features,
        label_col="y",
        configuration=configuration,
        weight_col="weight" if weighted else None,
        group_col="unit" if kind == "random_intercept" else None,
        batch_size=64,
        reduction="sum",
        l2_strength=strength,
    ) as evaluator:
        descriptor = evaluator.descriptor
        result = minimize_lbfgsb(
            evaluator.evaluate,
            initial,
            bounds=limits,
            max_iterations=300,
            gradient_tolerance=1e-5,
            function_tolerance=1e-14,
        )
    parameters = list(result.parameters)
    theta = parameters
    if kind == "nonlinear_growth":
        amplitude, rate, offset, scale = parameters
        if amplitude >= 0:
            raise AssertionError("Growth requires the declared negative decay amplitude")
        log_amplitude = (
            12.0
            if amplitude == -math.exp(12)
            else -12.0
            if amplitude == -math.exp(-12)
            else math.log(-amplitude)
        )
        theta = [offset + amplitude, log_amplitude, rate, scale]
    output = {
        "parameters": theta,
        "backend_parameters": parameters,
        "observed_objective": result.evaluation.value,
        "diagnostics": {
            "converged": result.converged,
            "status": result.status,
            "message": result.message,
            "iterations": result.iterations,
            "objective_calls": result.objective_calls,
            "raw_gradient_inf": result.gradient_inf_norm,
            "projected_gradient_inf": result.projected_gradient_inf_norm,
            "row_count": result.evaluation.row_count,
            "weight_sum": result.evaluation.weight_sum,
            "partition_count": result.evaluation.partition_count,
            "unit_count": getattr(result.evaluation, "unit_count", 0),
        },
        "model_descriptor": descriptor,
        "predictions": [],
    }
    if not result.converged:
        return output
    reference = prediction_reference(case, theta)
    if kind == "random_intercept":
        # The current Torch interface declares new_group_mean, not a history-aware
        # forecast API. Check that real target; retain conditional moments as a
        # separately labeled mathematical derivation from the fitted parameters.
        unseen = [row for row in case["future"] if row["cohort"] == "unseen"]
        future = sql_frame(spark, unseen, ["row_id", "unit"], partitions)
        predicted = predict_dataframe(
            future,
            model,
            parameters,
            feature_columns={},
            target="new_group_mean",
            prediction_col="prediction",
            expected_descriptor=descriptor,
        ).collect()
        if len(predicted) != len(unseen) or any(
            abs(row.prediction - theta[0]) > 1e-8 for row in predicted
        ):
            raise AssertionError("Actual Torch new-group mean differs from its declared target")
        output["predictions"] = reference
        output["prediction_scope"] = (
            "Torch API new-group mean checked; history-aware means/variances are explicit "
            "mathematical references, not a Torch forecast API"
        )
    else:
        future = sql_frame(spark, case["future"], ["row_id"] + list(features.values()), partitions)
        target = {
            "normal_mle": "conditional_mean",
            "linear_all_coordinate_map": "conditional_mean",
            "nonlinear_growth": "conditional_mean",
        }[kind]
        predicted = predict_dataframe(
            future,
            model,
            parameters,
            feature_columns=features,
            configuration=configuration,
            target=target,
            prediction_col="prediction",
            expected_descriptor=descriptor,
        ).collect()
        means = {row.row_id: row.prediction for row in predicted}
        if (
            len(means) != len(predicted)
            or len(predicted) != len(reference)
            or set(means) != {row["row_id"] for row in reference}
        ):
            raise AssertionError("Torch prediction identity coverage differs")
        for row in reference:
            if not math.isclose(row["mean"], means[row["row_id"]], rel_tol=1e-7, abs_tol=1e-7):
                raise AssertionError(
                    "Actual Torch point target differs from the independent formula"
                )
        output["predictions"] = reference
        output["prediction_scope"] = (
            "Actual Torch response-free mean checked; observation variances derived "
            "explicitly from fitted scale"
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=["native", "torch"])
    parser.add_argument(
        "--fixtures", type=Path, default=Path(__file__).with_name("fixtures") / "smoke.json"
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--study", choices=["sim-001", "sim-002", "sim-006", "sim-008"], required=True
    )
    parser.add_argument("--replicate", type=int, default=0)
    parser.add_argument("--partitions", type=int, default=2)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a new output path; existing study evidence is retained")
    if not 1 <= args.partitions <= 8 or args.replicate < 0:
        raise ValueError("Choose 1..8 partitions and a nonnegative replication index")
    if args.backend == "native" and args.manifest is None:
        raise ValueError("Native studies require an explicit prepared manifest")
    with args.fixtures.open("rb") as stream:
        fixture_bytes = stream.read(4 * 1024 * 1024 + 1)
    if len(fixture_bytes) > 4 * 1024 * 1024:
        raise ValueError("Study fixture exceeds its 4 MiB input bound")
    bundle = json.loads(fixture_bytes)
    canonical(bundle)
    if bundle.get("kind") != "original-shared-modeling-fixtures":
        raise ValueError("Unsupported fixture bundle")
    cases = [
        case
        for case in bundle["cases"]
        if case["study"] == args.study and case["replicate"] == args.replicate
    ]
    if len(cases) != 2:
        raise ValueError("Select exactly one prepared replication and its two changed scenarios")
    expected_case = {
        "sim-001": "normal_mle",
        "sim-002": "linear_all_coordinate_map",
        "sim-006": "nonlinear_growth",
        "sim-008": "random_intercept",
    }[args.study]
    if len({case["scenario"] for case in cases}) != 2:
        raise ValueError("The shard must contain two distinct declared scenarios")
    for case in cases:
        if (
            case["case"] != expected_case
            or not 1 <= len(case["methods"]) <= 2
            or not 1 <= len(case["training"]) <= 4096
            or not 1 <= len(case["future"]) <= 128
        ):
            raise ValueError("Study case kind, method count or fixture size differs")
        training_ids = {row["row_id"] for row in case["training"]}
        future_ids = {row["row_id"] for row in case["future"]}
        if (
            len(training_ids) != len(case["training"])
            or len(future_ids) != len(case["future"])
            or training_ids & future_ids
        ):
            raise ValueError("Study row identities must be unique and train/future disjoint")

    identity = (
        installed("ds60_spark_tmbad", "ds60-spark-tmbad")
        if args.backend == "native"
        else installed("ds60_spark_likelihood", "ds60-spark-likelihood")
    )
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("Original modeling simulation study").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    report = {
        "schema_version": 1,
        "kind": "original-spark-modeling-study",
        "status": "incomplete",
        "backend": args.backend,
        "study": args.study,
        "replicate": args.replicate,
        "partitions": args.partitions,
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "generator_sha256": bundle["generator_sha256"],
        "seed": bundle["seed"],
        "optimizer_settings": {
            "max_iterations": 300,
            "gradient_tolerance": 1e-5,
            "function_tolerance": 0.0 if args.backend == "native" else 1e-14,
            "reduction": "sum",
            "fit_qualification": "status plus canonical projected score <=1e-5",
        },
        "package_identity": identity,
        "study_source_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("run_spark.py", "study_support.py")
        },
        "spark_version": spark.version,
        "runtime_versions": {
            "python": platform.python_version(),
            "machine": platform.machine(),
            "java": spark._jvm.java.lang.System.getProperty("java.version"),
            **(
                {name: importlib.metadata.version(name) for name in ("torch", "numpy", "scipy")}
                if args.backend == "torch"
                else {}
            ),
        },
        "records": [],
        "scope": "small synthetic actual Spark shard; no Monte Carlo or cluster-scaling conclusion",
    }
    failure = None
    started = time.monotonic()
    api = None
    try:
        if args.backend == "native":
            if args.manifest is None:
                raise ValueError("Native studies require an explicit prepared manifest")
            from ds60_spark_tmbad import PreparedRuntime, SparkTMBad

            api = SparkTMBad(PreparedRuntime.from_manifest(args.manifest))
            probe = api.probe(spark, "normal")
            if not probe.get("passed"):
                raise AssertionError("Native preflight did not complete")
            report["artifact_identity"] = api.runtime.identity("normal")
            from ds60_spark_tmbad import ModelSpec

            control_rows = [{"row_id": i, "y": float(i + 1)} for i in range(4)]
            control_frame = sql_frame(spark, control_rows, ["row_id", "y"], args.partitions)
            control_fit = api.fit_shared(
                control_frame,
                ModelSpec("normal", {"y": "y"}, id_columns=["row_id"]),
                options={"initial_parameters": [2.5, 0.5 * math.log(1.25)]},
            )
            reference_value, _ = objective(
                {"case": "normal_mle", "training": control_rows}, [2.5, 0.5 * math.log(1.25)]
            )
            if not control_fit.model["fit"]["converged"] or not math.isclose(
                control_fit.model["fit"]["loss"], reference_value, rel_tol=1e-10, abs_tol=1e-10
            ):
                raise AssertionError("Actual native control failed its analytic likelihood check")
            report["backend_control"] = {"probe": probe, "normal_fit": control_fit.model["fit"]}
        else:
            from ds60_spark_likelihood.dataframe import DataFrameObjective

            control = sql_frame(
                spark,
                [{"row_id": i, "y": float(i + 1)} for i in range(4)],
                ["row_id", "y"],
                args.partitions,
            )
            with DataFrameObjective(
                control, "normal_mean", feature_columns={}, label_col="y"
            ) as evaluator:
                evaluated = evaluator.evaluate([2.5, 0.5 * math.log(1.25)])
            reference_value, _ = objective(
                {"case": "normal_mle", "training": [{"y": float(i + 1)} for i in range(4)]},
                [2.5, 0.5 * math.log(1.25)],
            )
            if (
                max(abs(x) for x in evaluated.gradient) > 1e-9
                or evaluated.row_count != 4
                or not math.isclose(evaluated.value, reference_value, rel_tol=1e-10, abs_tol=1e-10)
            ):
                raise AssertionError(
                    "Actual Torch control did not match the analytic stationary point"
                )
            report["backend_control"] = {
                "actual_objective": evaluated.value,
                "actual_gradient": evaluated.gradient,
                "rows": 4,
            }
        for case in cases:
            for method in case["methods"]:
                record = {
                    "scenario": case["scenario"],
                    "method": method["id"],
                    "l2_strength": method["l2_strength"],
                    "truth": case["truth"],
                    "canonical_initial": case["initial"],
                    "training_rows": len(case["training"]),
                    "future_rows": len(case["future"]),
                    "case_sha256": digest(case),
                    "status": "started",
                }
                report["records"].append(record)
                before = time.monotonic()
                fitted = (
                    native_fit(spark, api, case, method["l2_strength"], args.partitions)
                    if args.backend == "native"
                    else torch_fit(spark, case, method["l2_strength"], args.partitions)
                )
                value, gradient = objective(case, fitted["parameters"], method["l2_strength"])
                record.update(fitted)
                if fitted["diagnostics"]["row_count"] != len(case["training"]):
                    raise AssertionError(
                        "Actual backend observation coverage differs from the fixture"
                    )
                record["elapsed_seconds"] = time.monotonic() - before
                if not math.isclose(
                    value, fitted["observed_objective"], rel_tol=1e-7, abs_tol=1e-7
                ):
                    raise AssertionError(
                        "Backend fit value differs from the independent scientific target"
                    )
                score = projected_score(fitted["parameters"], gradient, case["case"])
                record["canonical_reference_objective"] = value
                record["canonical_reference_gradient"] = gradient
                record["canonical_projected_score_inf"] = score
                qualified = fitted["diagnostics"]["converged"] and score <= 1e-5
                record["status"] = "passed" if qualified else "failed"
                if qualified:
                    predictions = prediction_reference(case, fitted["parameters"])
                    observed = {p["row_id"]: p for p in fitted["predictions"]}
                    if len(observed) != len(fitted["predictions"]) or set(observed) != {
                        p["row_id"] for p in predictions
                    }:
                        raise AssertionError("Actual prediction row identity/cardinality differs")
                    for p in predictions:
                        if p["row_id"] not in observed or any(
                            not math.isclose(
                                observed[p["row_id"]][field], p[field], rel_tol=1e-6, abs_tol=1e-6
                            )
                            for field in ("mean", "variance")
                        ):
                            raise AssertionError(
                                "Predictive target differs from its independent declared moments"
                            )
                    record["future_metrics"] = forecast_metrics(case, fitted["predictions"])
                else:
                    record["failure_category"] = "fit_not_certified_by_status_and_canonical_score"
        if (
            installed(
                "ds60_spark_tmbad" if args.backend == "native" else "ds60_spark_likelihood",
                "ds60-spark-tmbad" if args.backend == "native" else "ds60-spark-likelihood",
            )
            != identity
        ):
            raise AssertionError("Installed source changed during the study")
        if args.backend == "native":
            api.runtime.verify_files()
        report["status"] = "completed"
        report["fit_failures"] = sum(row["status"] == "failed" for row in report["records"])
    except BaseException as error:
        failure = error
        report["status"] = "interrupted"
        report["failure_type"] = type(error).__name__
        report["failure_message_sha256"] = hashlib.sha256(str(error).encode()).hexdigest()
        if report["records"] and report["records"][-1]["status"] == "started":
            report["records"][-1].update(
                status="failed",
                failure_category="unclassified_execution_failure_requires_investigation",
            )
    finally:
        try:
            spark.stop()
        except Exception as error:
            report["cleanup_failure_type"] = type(error).__name__
            if failure is None:
                failure = error
                report["status"] = "interrupted"
        report["elapsed_seconds"] = time.monotonic() - started
        body = canonical(report) + b"\n"
        if len(body) > 4 * 1024 * 1024:
            raise ValueError("Study shard report exceeds 4 MiB")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(body)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "backend": args.backend,
                    "study": args.study,
                    "path": str(args.output),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "fit_failures": report.get("fit_failures"),
                }
            )
        )
    if failure is not None:
        raise failure


if __name__ == "__main__":
    main()
