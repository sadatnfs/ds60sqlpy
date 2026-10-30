"""Validate extended fitted-target provenance without rerunning its data or optimizer."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ._json import ContractError
from ._targets import (
    COORDINATES,
    LEGACY,
    SUMMED,
    active_bounds,
    close,
    effective_fixed_check,
    fixed_parameters,
    free_count,
    legacy_penalty,
    number,
    parameters,
    penalties,
    plan_digest,
    regularization,
    target_digest,
    validate_solver,
)
from .runtime import _fields, _integer, _object, _sha

COMPONENTS = {
    "data_sum",
    "gaussian_quadratic_sum",
    "gaussian_log_normalizer_sum",
    "l1_sum",
    "legacy_l2_reduced",
    "denominator",
    "total_reduced",
}
TARGET_FIELDS = {
    "schema_version",
    "coordinate_system",
    "normalization",
    "regularization",
    "fixed_parameters",
    "legacy_l2_strength",
    "plan_digest",
    "target_spec_digest",
    "effective_initial_parameters",
    "free_parameter_count",
    "solver",
    "loss_components",
    "stationarity",
    "proximal_trace",
}


def validate_ledger(value: Any, row_count: int) -> None:
    ledger = _object(value, "data ledger")
    _fields(ledger, {"count", "xor", "sum"}, "data ledger")
    _integer(ledger["count"], 0, 2**53 - 1, "ledger count")
    if ledger["count"] != row_count:
        raise ContractError("Data ledger count differs from row count")
    for field in ("xor", "sum"):
        text = ledger[field]
        if (
            not isinstance(text, str)
            or not 1 <= len(text) <= 64
            or any(char not in "0123456789abcdef" for char in text)
        ):
            raise ContractError("Data ledger hashes must be bounded lowercase hexadecimal")


def validate_components(
    value: Any,
    descriptor: Mapping[str, Any],
    theta: list[float],
    reg: Mapping[str, Any] | None,
    legacy: float,
    denominator: float,
) -> dict[str, Any]:
    components = _object(value, "loss components")
    _fields(components, COMPONENTS, "loss components")
    for field, item in components.items():
        number(
            item,
            field,
            minimum=0
            if field in {"gaussian_quadratic_sum", "l1_sum", "legacy_l2_reduced"}
            else None,
        )
    quadratic, normalizer, l1, _, _ = penalties(descriptor, theta, reg)
    legacy_value = legacy_penalty(theta, legacy)
    close(components["denominator"], denominator, "normalization denominator")
    if components["denominator"] <= 0:
        raise ContractError("Normalization denominator must be positive")
    close(components["gaussian_quadratic_sum"], quadratic, "Gaussian prior quadratic")
    close(components["gaussian_log_normalizer_sum"], normalizer, "Gaussian prior normalizer")
    close(components["l1_sum"], l1, "L1 value")
    close(components["legacy_l2_reduced"], legacy_value, "legacy L2 value")
    total = (components["data_sum"] + quadratic + normalizer + l1) / denominator + legacy_value
    close(components["total_reduced"], total, "target objective")
    return components


def validate_target(
    value: Any, descriptor: Mapping[str, Any], theta: list[float], fit: Mapping[str, Any]
) -> None:
    target = _object(value, "fitted target")
    _fields(target, TARGET_FIELDS, "fitted target")
    _integer(target["schema_version"], 1, 1, "fitted target schema")
    if target["coordinate_system"] != COORDINATES:
        raise ContractError("Unknown fitted target coordinate system")
    reg = (
        None
        if target["regularization"] is None
        else regularization(target["regularization"], descriptor)
    )
    fixed = fixed_parameters(target["fixed_parameters"], descriptor)
    legacy = number(target["legacy_l2_strength"], "legacy L2 strength", minimum=0)
    if reg is not None and legacy != 0:
        raise ContractError("Saved target mixes legacy and named penalties")
    normalization = SUMMED if reg is not None else LEGACY
    plan = plan_digest(descriptor, reg, fixed)
    _sha(target["plan_digest"], "plan digest")
    _sha(target["target_spec_digest"], "target specification digest")
    if (
        target["normalization"] != normalization
        or target["plan_digest"] != plan
        or target["target_spec_digest"] != target_digest(plan, normalization, legacy)
    ):
        raise ContractError("Saved target specification digest differs")
    effective_fixed_check(theta, descriptor, fixed)
    if not isinstance(target["effective_initial_parameters"], list):
        raise ContractError("Effective initial parameters must be a JSON array")
    initial = parameters(
        target["effective_initial_parameters"], descriptor, "effective initial parameters"
    )
    effective_fixed_check(initial, descriptor, fixed)
    free = free_count(descriptor, fixed)
    _integer(target["free_parameter_count"], 0, len(theta), "free parameter count")
    if target["free_parameter_count"] != free:
        raise ContractError("Saved free parameter count differs")
    if not {"reduction", "l2_strength", "data_ledger"}.issubset(fit):
        raise ContractError("Schema2 fit requires reduction, L2 and a complete data ledger")
    validate_ledger(fit["data_ledger"], fit["row_count"])
    if fit["l2_strength"] != legacy:
        raise ContractError("Saved legacy L2 strength differs from fit diagnostics")
    denominator = fit["weight_sum"] if fit["reduction"] == "weighted_mean" else 1.0
    components = validate_components(
        target["loss_components"], descriptor, theta, reg, legacy, denominator
    )
    close(fit["loss"], components["total_reduced"], "fitted target loss")
    has_l1 = bool(reg and reg["l1"])
    solver = validate_solver(target["solver"], has_l1=has_l1, has_regularization=reg is not None)
    if (
        fit["iterations"] > solver["max_iterations"]
        or fit["objective_calls"] > solver["max_evaluations"]
    ):
        raise ContractError("Saved fit exceeded its solver budgets")
    if fit["active_bounds"] != active_bounds(theta, descriptor, fixed):
        raise ContractError("Saved active-bound mask differs from the accepted parameters")
    stationarity = _object(target["stationarity"], "stationarity")
    _fields(
        stationarity,
        {"kind", "summed_inf", "reduced_inf", "tolerance", "tolerance_units"},
        "stationarity",
    )
    if stationarity["kind"] != ("l1_box_kkt" if has_l1 else "box_gradient"):
        raise ContractError("Wrong saved stationarity kind")
    summed = number(stationarity["summed_inf"], "summed stationarity", minimum=0)
    reduced = number(stationarity["reduced_inf"], "reduced stationarity", minimum=0)
    close(reduced, summed / denominator, "stationarity scaling")
    method = solver["method"]
    tolerance = number(stationarity["tolerance"], "stationarity tolerance", positive=True)
    expected_tolerance = (
        solver["gradient_tolerance"] if method == "bfgs" else solver["kkt_tolerance"]
    )
    if tolerance != expected_tolerance or stationarity["tolerance_units"] != (
        "reduced_objective" if method == "bfgs" else "summed_target"
    ):
        raise ContractError("Saved convergence tolerance or its units differ")
    if method == "bfgs":
        close(fit["projected_gradient_inf"], reduced, "box-gradient stationarity")
    if fit["converged"] and (reduced if method == "bfgs" else summed) > tolerance:
        raise ContractError("Converged flag contradicts the target stationarity criterion")
    successful = (
        "all_parameters_fixed"
        if free == 0
        else ("projected_gradient_tolerance" if method == "bfgs" else "summed_target_kkt_tolerance")
    )
    if fit["converged"] and fit["status"] != successful:
        raise ContractError("Converged status does not match the declared solver")
    failures = (
        {
            "maximum_iterations",
            "maximum_evaluations",
            "line_search_failed",
            "step_stalled_without_stationarity",
            "function_stalled_without_stationarity",
        }
        if method == "bfgs"
        else {
            "maximum_iterations",
            "maximum_evaluations",
            "step_stalled_without_kkt",
            "proximal_backtracking_failed",
        }
    )
    if not fit["converged"] and fit["status"] not in failures:
        raise ContractError("Failed fit has an unsupported or successful solver status")
    trace = target["proximal_trace"]
    if not isinstance(trace, list) or len(trace) > 1000:
        raise ContractError("Proximal trace must be a bounded array")
    if method == "bfgs":
        if trace:
            raise ContractError("BFGS fit cannot contain a proximal trace")
    else:
        if fit["trace"] or len(trace) != fit["iterations"]:
            raise ContractError("Proximal fit has fabricated BFGS history or missing iterations")
        previous_calls = 0
        for iteration, raw in enumerate(trace, 1):
            entry = _object(raw, "proximal trace record")
            _fields(
                entry,
                {
                    "iteration",
                    "loss",
                    "summed_kkt_inf",
                    "reduced_kkt_inf",
                    "relative_step_inf",
                    "step_size",
                    "backtracks",
                    "objective_calls",
                },
                "proximal trace record",
            )
            if _integer(entry["iteration"], 1, 1000, "proximal iteration") != iteration:
                raise ContractError("Proximal trace iteration order differs")
            number(entry["loss"], "proximal trace loss")
            for name in ("summed_kkt_inf", "reduced_kkt_inf", "relative_step_inf"):
                number(entry[name], name, minimum=0)
            number(entry["step_size"], "proximal step", positive=True)
            if not solver["minimum_step"] <= entry["step_size"] <= solver["maximum_step"]:
                raise ContractError("Proximal trace step is outside its declared limits")
            _integer(entry["backtracks"], 0, solver["max_backtracks"], "proximal backtracks")
            calls = _integer(
                entry["objective_calls"], 1, solver["max_evaluations"], "proximal call count"
            )
            if calls <= previous_calls or calls > fit["objective_calls"]:
                raise ContractError("Proximal trace objective counts differ")
            previous_calls = calls
            close(
                entry["reduced_kkt_inf"], entry["summed_kkt_inf"] / denominator, "trace KKT scaling"
            )
        if trace:
            close(trace[-1]["loss"], components["total_reduced"], "final proximal loss")
            close(trace[-1]["summed_kkt_inf"], summed, "final proximal summed KKT")
            close(trace[-1]["reduced_kkt_inf"], reduced, "final proximal reduced KKT")
    if free == 0 and (
        not fit["converged"]
        or fit["iterations"] != 0
        or fit["objective_calls"] != 1
        or fit["trace"]
        or trace
        or summed != 0
        or reduced != 0
        or fit["projected_gradient_inf"] != 0
    ):
        raise ContractError(
            "All-fixed fit must record one actual evaluation and no optimization history"
        )
