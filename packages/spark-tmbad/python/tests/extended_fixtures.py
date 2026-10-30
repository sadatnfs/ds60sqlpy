"""Synthetic wire-contract fixtures with a transparent four-row normal objective."""

import math

from ds60_spark_tmbad import ModelSpec, PreparedRuntime
from ds60_spark_tmbad._targets import (
    active_bounds,
    kkt,
    legacy_penalty,
    option_target,
    parameter_digest,
    penalties,
    resolved_solver,
)
from test_contracts import manifest, model


def runtime(version="0.2.0"):
    value = manifest()
    value["package_version"] = version
    value["models"][0]["forecast"] = value["models"][0]["predict"].copy()
    return PreparedRuntime(value)


def regularization(*, lasso=True):
    return {
        "schema_version": 1,
        "coordinate_system": "native_optimizer_parameters",
        "normalization": "summed_likelihood_target",
        "gaussian": {"mu": {"mean": 1, "precision": 2 if lasso else 4}},
        "l1": {"mu": 1} if lasso else {},
    }


def evaluation(selected_runtime, point, options):
    descriptor = selected_runtime.descriptor("normal")
    reduction = options.get("reduction", "sum")
    denominator = 4.0 if reduction == "weighted_mean" else 1.0
    mu, log_sigma = point
    residuals = [y - mu for y in (1, 2, 4, 7)]
    inverse = math.exp(-2 * log_sigma)
    squares = sum(value * value for value in residuals)
    data_value = 4 * (log_sigma + 0.5 * math.log(2 * math.pi)) + 0.5 * squares * inverse
    data_gradient = [-sum(residuals) * inverse, 4 - squares * inverse]
    q, c, l1, prior, intervals = penalties(descriptor, point, options.get("regularization"))
    legacy = options.get("l2_strength", 0.0)
    legacy_value = legacy_penalty(point, legacy)
    smooth = [data_gradient[i] + prior[i] + legacy * point[i] * denominator for i in range(2)]
    total = (data_value + q + c + l1) / denominator + legacy_value
    fixed = options.get("fixed_parameters", {})
    residual = kkt(point, smooth, intervals, descriptor, fixed)
    return {
        "schema_version": 1,
        "kind": "spark-tmbad-evaluation",
        "package_version": selected_runtime.manifest["package_version"],
        "model_id": "normal",
        "model_digest": descriptor["digest"],
        "artifact_identity": selected_runtime.identity("normal"),
        "parameter_names": descriptor["parameter_names"],
        "parameters": point,
        "parameter_digest": parameter_digest(descriptor, point),
        "target_spec_digest": option_target(descriptor, options)[2],
        "reduction": reduction,
        "weight_kind": "observation",
        "row_count": 4,
        "unit_count": 0,
        "weight_sum": 4.0,
        "partition_count": 2,
        "data_ledger": {"count": 4, "xor": "1", "sum": "2"},
        "loss_components": {
            "data_sum": data_value,
            "gaussian_quadratic_sum": q,
            "gaussian_log_normalizer_sum": c,
            "l1_sum": l1,
            "legacy_l2_reduced": legacy_value,
            "denominator": denominator,
            "total_reduced": total,
        },
        "data_gradient_sum": data_gradient,
        "smooth_gradient_sum": smooth,
        "smooth_gradient_reduced": [value / denominator for value in smooth],
        "l1_subgradient_sum": intervals,
        "fixed_parameters": fixed,
        "summed_kkt_inf": residual,
        "reduced_kkt_inf": residual / denominator,
    }


def fitted_document(selected_runtime, *, proximal=True, reduction="sum", all_fixed=False):
    descriptor = selected_runtime.descriptor("normal")
    denominator = 4.0 if reduction == "weighted_mean" else 1.0
    point = [2.5 if proximal else 2.25, 0.0]
    options = {
        "initial_parameters": [0.0, 0.0] if proximal else point.copy(),
        "reduction": reduction,
        "regularization": regularization(lasso=proximal),
        "fixed_parameters": {"log_sigma": 0.0},
        "solver": {"method": "proximal_gradient", "initial_step": denominator / 6}
        if proximal
        else {"method": "bfgs"},
    }
    if all_fixed:
        proximal = False
        point = [2.0, 0.0]
        options = {
            "initial_parameters": [0.0, 0.0],
            "fixed_parameters": {"mu": 2.0, "log_sigma": 0.0},
            "reduction": reduction,
            "l2_strength": 0.3,
            "solver": {"method": "bfgs"},
        }
    observed = evaluation(selected_runtime, point, options)
    document = model(selected_runtime)
    document.update(
        schema_version=2,
        package_version=selected_runtime.manifest["package_version"],
        parameters=point,
    )
    document["spec"] = ModelSpec("normal", {"y": "observation"}, id_columns=["row_id"]).to_dict()
    fit = document["fit"]
    smooth = observed["smooth_gradient_reduced"]
    fit.update(
        loss=observed["loss_components"]["total_reduced"],
        status="all_parameters_fixed"
        if all_fixed
        else "summed_target_kkt_tolerance"
        if proximal
        else "projected_gradient_tolerance",
        iterations=1 if proximal else 0,
        objective_calls=2 if proximal else 1,
        raw_gradient_inf=max(map(abs, smooth)),
        projected_gradient_inf=0.0 if all_fixed else abs(smooth[0]),
        active_bounds=active_bounds(point, descriptor, options["fixed_parameters"]),
        reduction=reduction,
        l2_strength=options.get("l2_strength", 0.0),
        data_ledger=observed["data_ledger"],
        rejected_candidates=0,
    )
    plan, normalization, digest = option_target(descriptor, options)
    solver = resolved_solver(options)
    trace = []
    if proximal:
        trace = [
            {
                "iteration": 1,
                "loss": fit["loss"],
                "summed_kkt_inf": 0.0,
                "reduced_kkt_inf": 0.0,
                "relative_step_inf": 1.0,
                "step_size": denominator / 6,
                "backtracks": 0,
                "objective_calls": 2,
            }
        ]
    document["target"] = {
        "schema_version": 1,
        "coordinate_system": "native_optimizer_parameters",
        "normalization": normalization,
        "regularization": options.get("regularization"),
        "fixed_parameters": options["fixed_parameters"],
        "legacy_l2_strength": options.get("l2_strength", 0.0),
        "plan_digest": plan,
        "target_spec_digest": digest,
        "effective_initial_parameters": point.copy() if all_fixed or not proximal else [0.0, 0.0],
        "free_parameter_count": 0 if all_fixed else 1,
        "solver": solver,
        "loss_components": observed["loss_components"],
        "stationarity": {
            "kind": "l1_box_kkt" if proximal else "box_gradient",
            "summed_inf": 0.0,
            "reduced_inf": 0.0,
            "tolerance": 1e-6,
            "tolerance_units": "summed_target" if proximal else "reduced_objective",
        },
        "proximal_trace": trace,
    }
    return document, options
