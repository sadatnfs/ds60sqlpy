"""Source-bound JSON models, without executable deserialization."""

from __future__ import annotations

import math
import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ._json import ContractError, copy_object
from .runtime import PreparedRuntime, _fields, _integer, _text
from .spec import ModelSpec


def validate_model(value: Mapping[str, Any], runtime: PreparedRuntime) -> dict[str, Any]:
    if not isinstance(runtime, PreparedRuntime):
        raise ContractError("Loading a model requires an explicit PreparedRuntime")
    model = copy_object(value)
    fields = {
        "schema_version",
        "kind",
        "package_version",
        "model_id",
        "model_digest",
        "artifact_identity",
        "parameters",
        "parameter_names",
        "spec",
        "fit",
    }
    if set(model) != fields:
        raise ContractError(f"Fitted model must contain exactly these fields: {sorted(fields)}")
    if type(model["schema_version"]) is not int or model["schema_version"] != 1:
        raise ContractError("Unsupported fitted-model schema_version")
    if model["kind"] != "spark-tmbad-model" or model["package_version"] != "0.1.0":
        raise ContractError("Expected a spark-tmbad-model for package 0.1.0")
    descriptor = runtime.descriptor(model["model_id"])
    if model["model_digest"] != descriptor["digest"]:
        raise ContractError("Fitted model source digest does not match the prepared model")
    if model["artifact_identity"] != runtime.identity(model["model_id"]):
        raise ContractError("Fitted model artifact identity does not match the prepared runtime")
    names = model["parameter_names"]
    if names != descriptor.get("parameter_names") or not isinstance(names, list) or not names:
        raise ContractError("Fitted parameter order does not match the prepared model")
    theta = model["parameters"]
    if not isinstance(theta, list) or len(theta) != len(names):
        raise ContractError("Fitted parameter dimension does not match the prepared model")
    if any(
        isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
        for x in theta
    ):
        raise ContractError("Fitted parameters must be finite numbers")
    bounds = descriptor.get("parameter_bounds")
    if not isinstance(bounds, list) or len(bounds) != len(theta):
        raise ContractError("Prepared model parameter bounds are malformed")
    for name, parameter, bound in zip(names, theta, bounds, strict=True):
        if not isinstance(bound, list) or len(bound) != 2:
            raise ContractError("Prepared model parameter bounds are malformed")
        low, high = bound
        if (low is not None and parameter < low) or (high is not None and parameter > high):
            raise ContractError(f"Fitted parameter is outside the prepared domain: {name}")
    if not isinstance(model["spec"], dict):
        raise ContractError("Fitted model spec must be a JSON object")
    _fields(
        model["spec"],
        {"model_id", "columns", "id_columns", "group_columns", "order_columns", "weight_column"},
        "fitted spec",
    )
    spec = ModelSpec.from_dict(model["spec"])
    if spec.model_id != model["model_id"]:
        raise ContractError("Fitted model and input spec select different model identities")
    spec.validate_descriptor(descriptor)
    if not isinstance(model["fit"], dict):
        raise ContractError("Fitted model diagnostics must be a JSON object")
    if type(model["fit"].get("converged")) is not bool:
        raise ContractError("Fitted model diagnostics require a boolean converged flag")
    _validate_fit(model["fit"], len(theta), descriptor["fit_kind"])
    return model


def _number(value: Any, field: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{field} must be a finite number")
    if minimum is not None and value < minimum:
        raise ContractError(f"{field} is below its lower bound")
    return value


def _validate_fit(fit: dict[str, Any], parameter_count: int, fit_kind: str) -> None:
    _fields(
        fit,
        {
            "converged",
            "status",
            "reason",
            "iterations",
            "objective_calls",
            "loss",
            "raw_gradient_inf",
            "projected_gradient_inf",
            "active_bounds",
            "row_count",
            "unit_count",
            "weight_sum",
            "trace",
        },
        "fit diagnostics",
        {"reduction", "l2_strength", "data_ledger", "rejected_candidates"},
    )
    _text(fit["status"], 128, "fit status")
    _text(fit["reason"], 4096, "fit reason")
    _integer(fit["iterations"], 0, 1000, "fit iterations")
    _integer(fit["objective_calls"], 1, 10000, "fit objective calls")
    if "rejected_candidates" in fit:
        _integer(fit["rejected_candidates"], 0, fit["objective_calls"], "rejected candidate count")
    _integer(fit["row_count"], 1, 2**53 - 1, "fit row count")
    _integer(fit["unit_count"], 0, 2**53 - 1, "fit unit count")
    if (
        fit["unit_count"] > fit["row_count"]
        or (fit_kind == "rows" and fit["unit_count"] != 0)
        or (fit_kind == "unit" and fit["unit_count"] < 1)
    ):
        raise ContractError("Fit unit count is inconsistent with the model factorization")
    _number(fit["loss"], "fit loss")
    for field in ("raw_gradient_inf", "projected_gradient_inf"):
        _number(fit[field], field, minimum=0)
    if _number(fit["weight_sum"], "fit weight mass") <= 0:
        raise ContractError("Fit weight mass must be positive")
    active = fit["active_bounds"]
    if not isinstance(active, list) or len(active) > parameter_count:
        raise ContractError("active_bounds must be a bounded parameter-index list")
    for index in active:
        _integer(index, 0, parameter_count - 1, "active bound index")
    if len(set(active)) != len(active):
        raise ContractError("active_bounds must not duplicate indices")
    trace = fit["trace"]
    if not isinstance(trace, list) or len(trace) > 1000:
        raise ContractError("Fit trace must be an array of at most 1000 entries")
    for entry in trace:
        if not isinstance(entry, dict):
            raise ContractError("Fit trace entries must be objects")
        _fields(
            entry,
            {
                "iteration",
                "loss",
                "raw_gradient_inf",
                "projected_gradient_inf",
                "step_inf",
                "objective_calls",
                "hessian_reset",
            },
            "fit trace entry",
        )
        _integer(entry["iteration"], 1, 1000, "trace iteration")
        _integer(entry["objective_calls"], 1, 10000, "trace objective calls")
        _number(entry["loss"], "trace loss")
        for field in ("raw_gradient_inf", "projected_gradient_inf", "step_inf"):
            _number(entry[field], field, minimum=0)
        if type(entry["hessian_reset"]) is not bool:
            raise ContractError("Trace hessian_reset must be boolean")
    if "reduction" in fit and fit["reduction"] not in ("sum", "weighted_mean"):
        raise ContractError("Unknown fitted reduction")
    if "l2_strength" in fit:
        _number(fit["l2_strength"], "fitted L2 strength", minimum=0)
    if "data_ledger" in fit:
        ledger = fit["data_ledger"]
        if not isinstance(ledger, dict):
            raise ContractError("Data ledger must be an object")
        _fields(ledger, {"count", "xor", "sum"}, "data ledger")
        _integer(ledger["count"], 0, 2**53 - 1, "ledger count")
        if ledger["count"] != fit["row_count"]:
            raise ContractError("Data ledger count differs from the fitted row count")
        for field in ("xor", "sum"):
            if (
                not isinstance(ledger[field], str)
                or re.fullmatch(r"[0-9a-f]{1,64}", ledger[field]) is None
            ):
                raise ContractError("Data ledger digests must be bounded hexadecimal strings")


def save_model(path: str | Path, raw: str, *, overwrite: bool) -> None:
    """Save one local JSON file; do not reinterpret URIs as remote storage."""
    if type(overwrite) is not bool:
        raise ContractError("overwrite must be an explicit boolean")
    if not isinstance(path, (str, Path)) or (isinstance(path, str) and "://" in path):
        raise ContractError("Model.save accepts a local filesystem path, not a storage URI")
    target = Path(path)
    # Do not grow an already bounded JSON document past the 4 MiB read limit.
    encoded = raw.encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            Path(temporary).replace(target)
        else:
            # A hard link publishes complete bytes atomically and fails if the
            # target appeared concurrently. Both paths are in the same directory.
            os.link(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
