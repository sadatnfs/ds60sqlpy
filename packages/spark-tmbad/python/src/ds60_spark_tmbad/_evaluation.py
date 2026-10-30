"""Strict bounded fixed-point evaluation responses, with no convergence fiction."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from ._json import ContractError, copy_object
from ._target_documents import validate_components, validate_ledger
from ._targets import (
    close,
    effective_fixed_check,
    kkt,
    number,
    option_target,
    parameter_digest,
    parameters,
    penalties,
)
from .runtime import PreparedRuntime, _fields, _integer

FIELDS = {
    "schema_version",
    "kind",
    "package_version",
    "model_id",
    "model_digest",
    "artifact_identity",
    "parameter_names",
    "parameters",
    "parameter_digest",
    "target_spec_digest",
    "reduction",
    "weight_kind",
    "row_count",
    "unit_count",
    "weight_sum",
    "partition_count",
    "data_ledger",
    "loss_components",
    "data_gradient_sum",
    "smooth_gradient_sum",
    "smooth_gradient_reduced",
    "l1_subgradient_sum",
    "fixed_parameters",
    "summed_kkt_inf",
    "reduced_kkt_inf",
}


def _vector(value: Any, size: int, field: str) -> list[float]:
    if not isinstance(value, list) or len(value) != size:
        raise ContractError(f"{field} must match the prepared parameter dimension")
    return [number(item, field) for item in value]


def validate_evaluation(
    value: Mapping[str, Any],
    runtime: PreparedRuntime,
    model_id: str,
    point: list[float],
    options: Mapping[str, Any],
) -> dict[str, Any]:
    result = copy_object(value)
    _fields(result, FIELDS, "fixed evaluation")
    _integer(result["schema_version"], 1, 1, "evaluation schema")
    descriptor = runtime.descriptor(model_id)
    if (
        result["kind"] != "spark-tmbad-evaluation"
        or result["package_version"] != runtime.manifest["package_version"]
    ):
        raise ContractError("Fixed evaluation kind/version differs from the selected runtime")
    if (
        result["model_id"] != model_id
        or result["model_digest"] != descriptor["digest"]
        or result["artifact_identity"] != runtime.identity(model_id)
    ):
        raise ContractError("Fixed evaluation source/artifact identity differs")
    if result["parameter_names"] != descriptor["parameter_names"]:
        raise ContractError("Fixed evaluation parameter names/order differ")
    if not isinstance(result["parameters"], list):
        raise ContractError("Evaluation coordinates must be a JSON array")
    observed = parameters(result["parameters"], descriptor)
    if observed != point or result["parameter_digest"] != parameter_digest(descriptor, point):
        raise ContractError("Fixed evaluation point or its digest differs")
    _, _, expected_target = option_target(descriptor, options)
    if result["target_spec_digest"] != expected_target:
        raise ContractError("Fixed evaluation target specification differs")
    reduction = options.get("reduction", "sum")
    if result["reduction"] != reduction:
        raise ContractError("Fixed evaluation reduction differs")
    expected_weight_kind = "observation" if descriptor["fit_kind"] == "rows" else "unit"
    if result["weight_kind"] != expected_weight_kind:
        raise ContractError("Fixed evaluation weight kind differs from model factorization")
    rows = _integer(result["row_count"], 1, 2**53 - 1, "evaluation row count")
    units = _integer(result["unit_count"], 0, rows, "evaluation unit count")
    if (expected_weight_kind == "observation" and units != 0) or (
        expected_weight_kind == "unit" and units < 1
    ):
        raise ContractError("Fixed evaluation unit count contradicts its factorization")
    weight = number(result["weight_sum"], "evaluation weight mass", positive=True)
    _integer(
        result["partition_count"],
        1,
        options.get("max_partitions", 4096),
        "evaluation partition count",
    )
    validate_ledger(result["data_ledger"], rows)
    denominator = weight if reduction == "weighted_mean" else 1.0
    reg = options.get("regularization")
    fixed = options.get("fixed_parameters", {})
    if result["fixed_parameters"] != fixed:
        raise ContractError("Fixed evaluation constraints differ")
    effective_fixed_check(point, descriptor, fixed)
    legacy = options.get("l2_strength", 0.0)
    validate_components(result["loss_components"], descriptor, point, reg, legacy, denominator)
    size = len(point)
    data = _vector(result["data_gradient_sum"], size, "data gradient")
    smooth = _vector(result["smooth_gradient_sum"], size, "summed smooth gradient")
    reduced = _vector(result["smooth_gradient_reduced"], size, "reduced smooth gradient")
    _, _, _, prior, intervals = penalties(descriptor, point, reg)
    reported_intervals = result["l1_subgradient_sum"]
    if not isinstance(reported_intervals, list) or len(reported_intervals) != size:
        raise ContractError("L1 subgradient intervals differ from parameter dimension")
    for i in range(size):
        expected = data[i] + prior[i] + legacy * point[i] * denominator
        close(smooth[i], expected, "smooth gradient decomposition")
        close(reduced[i], smooth[i] / denominator, "smooth gradient normalization")
        interval = _vector(reported_intervals[i], 2, "L1 subgradient interval")
        if interval[0] > interval[1]:
            raise ContractError("L1 subgradient interval is inverted")
        for observed_end, expected_end in zip(interval, intervals[i], strict=True):
            close(observed_end, expected_end, "L1 penalty subgradient")
        if (
            reg
            and reg["l1"].get(descriptor["parameter_names"][i], 0) > 0
            and reg["l1"][descriptor["parameter_names"][i]] / denominator == 0
        ):
            raise ContractError("Selected L1 disappears under the reported normalization")
    expected_kkt = kkt(point, smooth, intervals, descriptor, fixed)
    number(result["summed_kkt_inf"], "summed KKT", minimum=0)
    number(result["reduced_kkt_inf"], "reduced KKT", minimum=0)
    close(result["summed_kkt_inf"], expected_kkt, "summed constrained KKT")
    close(result["reduced_kkt_inf"], expected_kkt / denominator, "reduced constrained KKT")
    if not math.isfinite(expected_kkt):
        raise ContractError("Fixed evaluation KKT is not representable")
    return result
