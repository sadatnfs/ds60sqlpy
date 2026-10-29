"""Exact standalone wheel and numerical acceptance inside the native scientific gate."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from scripts.docker_registry import ReleaseError


def package_sources(root: Path) -> dict[str, str]:
    folder = root / "packages/spark-likelihood/src"
    return {
        path.relative_to(folder).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((folder / "ds60_spark_likelihood").rglob("*.py"))
    }


def bounded_error(value: Any, maximum: float, label: str) -> None:
    if type(value) not in {int, float} or not math.isfinite(value) or not 0 <= value <= maximum:
        raise ReleaseError("Standalone package failed numerical acceptance: " + label)


def validate_package(
    row: dict[str, Any], specification: dict[str, Any], architecture: str, root: Path
) -> None:
    contract = specification["package"]
    identity = row.get("identity", {})
    source = package_sources(root)
    expected_path = "/usr/local/lib/python3.12/site-packages/ds60_spark_likelihood"
    if (
        not source
        or identity.get("distribution") != contract["distribution"]
        or identity.get("version") != contract["version"]
        or identity.get("package_path") != expected_path
        or identity.get("isolated_python") is not True
        or identity.get("classroom_imported") is not False
        or identity.get("r_dependency_required") is not False
        or identity.get("wheel_name")
        != f"ds60_spark_likelihood-{contract['version']}-py3-none-any.whl"
    ):
        raise ReleaseError("Standalone package import/metadata isolation is incomplete")
    wheel_hash = identity.get("wheel_sha256")
    if (
        not isinstance(wheel_hash, str)
        or len(wheel_hash) != 64
        or any(c not in "0123456789abcdef" for c in wheel_hash)
    ):
        raise ReleaseError("Standalone wheel digest is invalid")
    if any(
        identity.get(key) != source
        for key in ("installed_source", "declared_source", "wheel_source")
    ):
        raise ReleaseError("Standalone wheel/source/installed identities differ")
    workers = row.get("executor_imports", {})
    records = workers.get("records", [])
    if (
        workers.get("kind") != "package-executor-isolation"
        or workers.get("passed") is not True
        or workers.get("spark") != specification["runtime"]["spark"]
        or len(records) != 2
        or sorted(item.get("partition", -1) for item in records) != [0, 1]
    ):
        raise ReleaseError("Standalone package lacks both actual executor import probes")
    for record in records:
        if type(record.get("fixture_rows")) is not int or record["fixture_rows"] != 1:
            raise ReleaseError("Executor package-import fixture coverage differs")
        for key in (
            "distribution",
            "version",
            "package_path",
            "installed_source",
            "classroom_imported",
            "r_dependency_required",
        ):
            if record.get(key) != identity[key] or type(record.get(key)) is not type(identity[key]):
                raise ReleaseError("Executor imported a different standalone package")
    observations = row.get("observations", {})
    if set(observations) != set(contract["observations"]):
        raise ReleaseError("Standalone numerical/Spark/ML modes are incomplete")
    by_kind = {}
    for mode, expected in contract["observations"].items():
        observed = observations[mode]
        if (
            not isinstance(observed, list)
            or [item.get("kind") for item in observed] != expected
            or any(item.get("passed") is not True for item in observed)
        ):
            raise ReleaseError("Standalone check inventory differs: " + mode)
        isolated = observed[0]
        if (
            isolated.get("version") != contract["version"]
            or isolated.get("module_path") != expected_path + "/__init__.py"
            or isolated.get("classroom_imported") is not False
            or isolated.get("rscript_present") is not False
        ):
            raise ReleaseError("Standalone mode imported source or requires R")
        by_kind.update({item["kind"]: item for item in observed[1:]})
    limits = {
        "package-row-numerical": {
            "max_analytic_error": 1e-12,
            "max_nonlinear_gradient_error": 1e-7,
        },
        "package-unit-numerical": {
            "max_rank_one_value_gradient_error": 1e-10,
            "max_finite_difference_error": 1e-7,
            "max_hessian_oracle_error": 1e-7,
        },
        "package-prediction-optimizer": {
            "max_prediction_error": 1e-12,
            "custom_model_value_gradient_error": 1e-10,
            "gradient_inf_norm": 1e-6,
        },
        "package-custom-gamma-poisson": {
            "max_scipy_value_gradient_error": 1e-9,
            "max_poisson_limit_value_gradient_error": 1e-9,
            "serial_fit_parameter_error": 2e-5,
            "gradient_inf_norm": 1e-4,
        },
        "package-spark-custom-unit": {
            "max_scipy_value_gradient_error": 1e-9,
            "serial_fit_parameter_error": 2e-5,
            "gradient_inf_norm": 1e-4,
        },
    }
    for kind, measures in limits.items():
        for name, maximum in measures.items():
            bounded_error(by_kind[kind].get(name), maximum, kind + "/" + name)
    if (
        by_kind["package-row-numerical"].get("partition_batch_cases") != 12
        or by_kind["package-row-numerical"].get("invalid_cases_rejected") != 5
        or by_kind["package-unit-numerical"].get("rows") != 9
        or by_kind["package-unit-numerical"].get("units") != 3
    ):
        raise ReleaseError("Standalone mathematical fixture coverage differs")
    spark_rows = by_kind["package-spark-rows"]
    if [item.get("partitions") for item in spark_rows.get("partition_cases", [])] != [
        1,
        2,
        5,
    ] or spark_rows.get("caller_cache_preserved") is not True:
        raise ReleaseError("Standalone row partition/cache coverage is incomplete")
    for name in ("normal_mle", "weighted_logistic_fit"):
        bounded_error(spark_rows.get(name, {}).get("gradient_inf_norm"), 1e-6, name)
    units = by_kind["package-spark-units"]
    if (
        [item.get("partitions") for item in units.get("layouts", [])] != [1, 2, 5]
        or any(
            units.get(key) is not True
            for key in (
                "caller_cache_preserved",
                "closed_objective_rejected",
                "duplicate_unit_rejected",
            )
        )
        or units.get("raw_data_collected") is not False
    ):
        raise ReleaseError("Standalone complete-unit partition/refusal coverage is incomplete")
    for layout in units["layouts"]:
        bounded_error(layout.get("error"), 1e-10, "complete-unit-layout")
        if layout.get("row_count") != 9 or layout.get("unit_count") != 3:
            raise ReleaseError("Standalone complete-unit membership differs")
    bounded_error(
        units.get("shared_group_fit", {}).get("oracle_parameter_error"), 2e-5, "shared-group-MLE"
    )
    bounded_error(
        units.get("shared_group_fit", {}).get("gradient_inf_norm"), 1e-5, "shared-group-score"
    )
    ml = by_kind["package-dataframe-ml"]
    runtime = ml.get("runtime", {})
    aliases = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64", "amd64": "amd64"}
    if (
        ml.get("checks") != contract["ml_checks"]
        or ml.get("classroom_imported") is not False
        or ml.get("r_required") is not False
        or ml.get("remote_cluster_executed") is not False
        or aliases.get(runtime.get("architecture")) != architecture
        or runtime.get("package") != contract["version"]
        or any(
            runtime.get(key) != specification["runtime"][key] for key in ("spark", "torch", "scipy")
        )
    ):
        raise ReleaseError("Standalone DataFrame/ML checks or native runtime differ")
    results = ml.get("results", {})
    for case in ("rows", "regression_custom", "complete_units", "custom_count_units"):
        bounded_error(results.get(case, {}).get("score"), 1e-5, "DataFrame/" + case)
    custom = results.get("custom_count_units", {})
    if (
        custom.get("row_count") != 13
        or custom.get("unit_count") != 6
        or custom.get("prediction_target") != "new_group_expected_count"
    ):
        raise ReleaseError("Custom count DataFrame lost its unit/prediction semantics")
    bounded_error(custom.get("value_gradient_oracle_error"), 1e-9, "custom-count-oracle")
    bounded_error(custom.get("serial_fit_parameter_error"), 2e-5, "custom-count-fit")
