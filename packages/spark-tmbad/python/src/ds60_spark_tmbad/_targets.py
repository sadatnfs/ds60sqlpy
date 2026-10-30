"""Named point-target validation and canonical cross-language identities."""

from __future__ import annotations

import hashlib
import math
import struct
from collections.abc import Mapping
from typing import Any

from ._json import ContractError, copy_object
from .runtime import _fields, _integer, _object, _sha

COORDINATES = "native_optimizer_parameters"
SUMMED = "summed_likelihood_target"
LEGACY = "legacy_post_reduction_l2"
EVALUATION_OPTIONS = {
    "reduction",
    "l2_strength",
    "regularization",
    "fixed_parameters",
    "batch_rows",
    "task_timeout_seconds",
    "max_partitions",
}
FIT_OPTIONS = EVALUATION_OPTIONS | {
    "initial_parameters",
    "max_iterations",
    "gradient_tolerance",
    "function_tolerance",
    "max_line_search",
    "solver",
}
PROXIMAL_INPUT = {
    "method",
    "kkt_tolerance",
    "kkt_tolerance_units",
    "initial_step",
    "maximum_step",
    "minimum_step",
    "backtrack_factor",
    "step_growth",
    "relative_step_tolerance",
}


def number(
    value: Any, label: str, *, minimum: float | None = None, positive: bool = False
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{label} must be a finite number")
    if (minimum is not None and value < minimum) or (positive and value <= 0):
        raise ContractError(f"{label} is outside its supported numeric domain")
    return float(value)


def close(actual: Any, expected: float, label: str) -> None:
    value = number(actual, label)
    if not math.isfinite(expected) or abs(value - expected) > 1e-9 * max(
        1.0, abs(value), abs(expected)
    ):
        raise ContractError(f"Inconsistent {label}")


def parameters(value: Any, descriptor: Mapping[str, Any], label: str = "parameters") -> list[float]:
    names = descriptor["parameter_names"]
    if isinstance(value, Mapping):
        mapping = copy_object(value)
        if set(mapping) != set(names):
            raise ContractError(f"{label} must name every prepared parameter exactly once")
        raw = [mapping[name] for name in names]
    elif isinstance(value, (list, tuple)):
        raw = copy_object({"values": list(value)})["values"]
    else:
        raise ContractError(f"{label} must be a complete vector or named mapping")
    if len(raw) != len(names):
        raise ContractError(f"{label} dimension differs from the prepared model")
    result = [number(item, label) for item in raw]
    for name, item, (lower, upper) in zip(
        names, result, descriptor["parameter_bounds"], strict=True
    ):
        if (lower is not None and item < lower) or (upper is not None and item > upper):
            raise ContractError(f"{label} is outside the prepared domain: {name}")
    return result


def fixed_parameters(value: Any, descriptor: Mapping[str, Any]) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise ContractError("fixed_parameters must be a named object")
    raw = copy_object(value)
    names = descriptor["parameter_names"]
    if set(raw) - set(names):
        raise ContractError("fixed_parameters names must match prepared parameters exactly")
    result = {}
    for name, (lower, upper) in zip(names, descriptor["parameter_bounds"], strict=True):
        if name in raw:
            item = number(raw[name], f"fixed parameter {name}")
            if (lower is not None and item < lower) or (upper is not None and item > upper):
                raise ContractError(f"Fixed parameter is outside the prepared domain: {name}")
            result[name] = item
    return result


def regularization(value: Any, descriptor: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError("regularization must be an explicit named target object")
    raw = copy_object(value)
    _fields(
        raw,
        {"schema_version", "coordinate_system", "normalization", "gaussian", "l1"},
        "regularization",
    )
    _integer(raw["schema_version"], 1, 1, "regularization schema")
    if raw["coordinate_system"] != COORDINATES or raw["normalization"] != SUMMED:
        raise ContractError("Unsupported regularization coordinate measure or normalization")
    gaussian = _object(raw["gaussian"], "Gaussian priors")
    l1 = _object(raw["l1"], "selected L1")
    names = descriptor["parameter_names"]
    if (set(gaussian) | set(l1)) - set(names):
        raise ContractError("Regularization names must match prepared parameters exactly")
    canonical_gaussian = {}
    canonical_l1 = {}
    for name in names:
        if name in gaussian:
            entry = _object(gaussian[name], f"Gaussian prior {name}")
            _fields(entry, {"mean", "precision"}, f"Gaussian prior {name}")
            canonical_gaussian[name] = {
                "mean": number(entry["mean"], "Gaussian mean"),
                "precision": number(entry["precision"], "Gaussian precision", positive=True),
            }
        if name in l1:
            canonical_l1[name] = number(l1[name], "L1 strength", positive=True)
    return {
        "schema_version": 1,
        "coordinate_system": COORDINATES,
        "normalization": SUMMED,
        "gaussian": canonical_gaussian,
        "l1": canonical_l1,
    }


def option_object(
    value: Mapping[str, Any] | None, descriptor: Mapping[str, Any], *, evaluation: bool = False
) -> dict[str, Any]:
    raw = copy_object({} if value is None else value)
    _fields(
        raw,
        set() if evaluation else {"initial_parameters"},
        "evaluation options" if evaluation else "fit options",
        EVALUATION_OPTIONS if evaluation else FIT_OPTIONS,
    )
    if "initial_parameters" in raw:
        if not isinstance(raw["initial_parameters"], list):
            raise ContractError("initial_parameters must be a native-order JSON array")
        raw["initial_parameters"] = parameters(
            raw["initial_parameters"], descriptor, "initial parameters"
        )
    if raw.get("reduction", "sum") not in {"sum", "weighted_mean"}:
        raise ContractError("Unknown likelihood reduction")
    if "l2_strength" in raw:
        raw["l2_strength"] = number(raw["l2_strength"], "legacy L2 strength", minimum=0)
    if "regularization" in raw:
        raw["regularization"] = regularization(raw["regularization"], descriptor)
        if raw.get("l2_strength", 0) != 0:
            raise ContractError("Nonzero legacy L2 cannot be combined with named regularization")
    if "fixed_parameters" in raw:
        raw["fixed_parameters"] = fixed_parameters(raw["fixed_parameters"], descriptor)
    for name, upper in {
        "batch_rows": 8192,
        "task_timeout_seconds": 3600,
        "max_partitions": 4096,
        "max_iterations": 1000,
        "max_line_search": 100,
    }.items():
        if name in raw:
            _integer(raw[name], 1, upper, name)
    for name in ("gradient_tolerance", "function_tolerance"):
        if name in raw:
            number(raw[name], name, minimum=0, positive=name == "gradient_tolerance")
    if not evaluation:
        resolved_solver(raw)
    return raw


def resolved_solver(options: Mapping[str, Any]) -> dict[str, Any]:
    reg = options.get("regularization")
    has_l1 = bool(reg and reg["l1"])
    raw = _object(options.get("solver", {}), "solver")
    method = raw.get("method", "proximal_gradient" if has_l1 else "bfgs")
    maximum = options.get("max_iterations", 100)
    backtracks = options.get("max_line_search", 25)
    result = {
        "method": method,
        "max_iterations": maximum,
        "max_evaluations": min(10000, 1 + maximum * (backtracks + 1)),
        "max_backtracks": backtracks,
    }
    if method == "bfgs":
        _fields(raw, set(), "BFGS solver", {"method"})
        if has_l1:
            raise ContractError("BFGS cannot optimize selected nonsmooth L1")
        result.update(
            gradient_tolerance=options.get("gradient_tolerance", 1e-6),
            function_tolerance=options.get("function_tolerance", 1e-12),
        )
    else:
        if method != "proximal_gradient" or reg is None or options.get("l2_strength", 0) != 0:
            raise ContractError(
                "Proximal gradient requires explicit named regularization and zero legacy L2"
            )
        _fields(raw, set(), "proximal solver", PROXIMAL_INPUT)
        result.update(
            kkt_tolerance=raw.get("kkt_tolerance", options.get("gradient_tolerance", 1e-6)),
            kkt_tolerance_units=raw.get("kkt_tolerance_units", "summed_target"),
            initial_step=raw.get("initial_step", 1.0),
            maximum_step=raw.get("maximum_step", 1e6),
            minimum_step=raw.get("minimum_step", 1e-14),
            backtrack_factor=raw.get("backtrack_factor", 0.5),
            step_growth=raw.get("step_growth", 1.5),
            relative_step_tolerance=raw.get("relative_step_tolerance", 1e-14),
        )
    validate_solver(result, has_l1=has_l1, has_regularization=reg is not None)
    return result


def validate_solver(value: Any, *, has_l1: bool, has_regularization: bool) -> dict[str, Any]:
    obj = _object(value, "resolved solver")
    common = {"method", "max_iterations", "max_evaluations", "max_backtracks"}
    method = obj.get("method")
    if method == "bfgs":
        _fields(obj, common | {"gradient_tolerance", "function_tolerance"}, "resolved BFGS solver")
        if has_l1:
            raise ContractError("Saved BFGS target cannot contain L1")
        number(obj["gradient_tolerance"], "gradient tolerance", positive=True)
        number(obj["function_tolerance"], "function tolerance", minimum=0)
    elif method == "proximal_gradient" and has_regularization:
        _fields(obj, common | (PROXIMAL_INPUT - {"method"}), "resolved proximal solver")
        for name in (
            "kkt_tolerance",
            "initial_step",
            "maximum_step",
            "minimum_step",
            "backtrack_factor",
            "step_growth",
            "relative_step_tolerance",
        ):
            number(obj[name], name, positive=True)
        if (
            obj["kkt_tolerance_units"] != "summed_target"
            or not 0 < obj["backtrack_factor"] < 1
            or obj["step_growth"] < 1
            or not obj["minimum_step"] <= obj["initial_step"] <= obj["maximum_step"]
        ):
            raise ContractError("Invalid proximal adaptation or KKT units")
    else:
        raise ContractError("Unknown or unsupported resolved solver")
    maximum = _integer(obj["max_iterations"], 1, 1000, "maximum iterations")
    backtracks = _integer(obj["max_backtracks"], 1, 100, "maximum backtracks")
    calls = _integer(obj["max_evaluations"], 1, 10000, "maximum evaluations")
    if calls != min(10000, 1 + maximum * (backtracks + 1)):
        raise ContractError("Resolved evaluation budget differs from iteration/backtracking limits")
    return obj


def _text_bytes(value: str) -> bytes:
    raw = value.encode("utf-8", errors="strict")
    return struct.pack(">i", len(raw)) + raw


def _double(value: float) -> bytes:
    return struct.pack(">d", 0.0 if value == 0 else value)


def parameter_digest(descriptor: Mapping[str, Any], theta: list[float]) -> str:
    data = (
        _text_bytes("spark-tmbad-parameters-v1")
        + _text_bytes(descriptor["digest"])
        + struct.pack(">i", len(theta))
    )
    return hashlib.sha256(data + b"".join(_double(item) for item in theta)).hexdigest()


def plan_digest(
    descriptor: Mapping[str, Any], reg: Mapping[str, Any] | None, fixed: Mapping[str, float]
) -> str:
    data = b"".join(
        _text_bytes(item)
        for item in (
            "spark-tmbad-named-target-v1",
            descriptor["digest"],
            COORDINATES,
            "d_selected_native_optimizer_coordinates",
            SUMMED,
            "none_penalty_only",
        )
    )
    names = descriptor["parameter_names"]
    data += struct.pack(">i", len(names))
    gaussian = {} if reg is None else reg["gaussian"]
    l1 = {} if reg is None else reg["l1"]
    for name, bounds in zip(names, descriptor["parameter_bounds"], strict=True):
        data += _text_bytes(name)
        for bound in bounds:
            data += bytes([bound is not None])
            if bound is not None:
                data += _double(bound)
        data += bytes([name in gaussian])
        if name in gaussian:
            data += _double(gaussian[name]["mean"]) + _double(gaussian[name]["precision"])
        data += _double(l1.get(name, 0)) + bytes([name in fixed])
        if name in fixed:
            data += _double(fixed[name])
    return hashlib.sha256(data).hexdigest()


def target_digest(plan: str, normalization: str, legacy_l2: float) -> str:
    _sha(plan, "plan digest")
    data = b"".join(
        _text_bytes(item) for item in ("spark-tmbad-fit-target-v2", plan, normalization)
    )
    return hashlib.sha256(data + _double(legacy_l2)).hexdigest()


def option_target(
    descriptor: Mapping[str, Any], options: Mapping[str, Any]
) -> tuple[str, str, str]:
    reg = options.get("regularization")
    plan = plan_digest(descriptor, reg, options.get("fixed_parameters", {}))
    normalization = SUMMED if reg is not None else LEGACY
    return plan, normalization, target_digest(plan, normalization, options.get("l2_strength", 0.0))


def penalties(
    descriptor: Mapping[str, Any], theta: list[float], reg: Mapping[str, Any] | None
) -> tuple[float, float, float, list[float], list[list[float]]]:
    gaussian = {} if reg is None else reg["gaussian"]
    l1 = {} if reg is None else reg["l1"]
    quadratic, normalizer, l1_value = [], [], []
    gradient, intervals = [], []
    for name, value in zip(descriptor["parameter_names"], theta, strict=True):
        entry = gaussian.get(name)
        if entry is not None:
            root_precision = math.sqrt(entry["precision"])
            difference = value - entry["mean"]
            scaled = (
                root_precision * difference
                if math.isfinite(difference)
                else root_precision * value - root_precision * entry["mean"]
            )
            gradient.append(number(root_precision * scaled, "Gaussian prior gradient"))
            quadratic.append(number(0.5 * scaled * scaled, "Gaussian prior value", minimum=0))
            normalizer.append(0.5 * (math.log(2 * math.pi) - math.log(entry["precision"])))
        else:
            gradient.append(0.0)
        strength = l1.get(name, 0.0)
        l1_value.append(number(strength * abs(value), "L1 value", minimum=0))
        derivative = math.copysign(strength, value)
        intervals.append([-strength, strength] if value == 0 else [derivative, derivative])
    try:
        result = math.fsum(quadratic), math.fsum(normalizer), math.fsum(l1_value)
    except OverflowError as exc:
        raise ContractError("Target penalty sum is not representable") from exc
    for item in result:
        number(item, "target penalty sum")
    return *result, gradient, intervals


def kkt(
    theta: list[float],
    smooth_gradient: list[float],
    intervals: list[list[float]],
    descriptor: Mapping[str, Any],
    fixed: Mapping[str, float],
) -> float:
    residuals = []
    for name, value, score, interval, (lower, upper) in zip(
        descriptor["parameter_names"],
        theta,
        smooth_gradient,
        intervals,
        descriptor["parameter_bounds"],
        strict=True,
    ):
        lo, hi = score + interval[0], score + interval[1]
        if name in fixed or (lower is not None and upper is not None and lower == upper):
            residual = 0.0
        elif lower is not None and value == lower:
            residual = max(0.0, -hi)
        elif upper is not None and value == upper:
            residual = max(0.0, lo)
        elif lo > 0:
            residual = lo
        elif hi < 0:
            residual = -hi
        else:
            residual = 0.0
        residuals.append(number(residual, "KKT residual", minimum=0))
    return max(residuals)


def legacy_penalty(theta: list[float], strength: float) -> float:
    if strength == 0:
        return 0.0
    root = math.sqrt(strength)
    terms = []
    for value in theta:
        scaled = root * value
        terms.append(number(0.5 * scaled * scaled, "legacy L2 value", minimum=0))
    try:
        return number(math.fsum(terms), "legacy L2 sum", minimum=0)
    except OverflowError as exc:
        raise ContractError("Legacy L2 sum is not representable") from exc


def effective_fixed_check(
    theta: list[float], descriptor: Mapping[str, Any], fixed: Mapping[str, float]
) -> None:
    for name, value in zip(descriptor["parameter_names"], theta, strict=True):
        if name in fixed and value != fixed[name]:
            raise ContractError(f"Parameter point differs from fixed value: {name}")


def free_count(descriptor: Mapping[str, Any], fixed: Mapping[str, float]) -> int:
    return sum(
        name not in fixed and (lower is None or upper is None or lower != upper)
        for name, (lower, upper) in zip(
            descriptor["parameter_names"], descriptor["parameter_bounds"], strict=True
        )
    )


def active_bounds(
    theta: list[float], descriptor: Mapping[str, Any], fixed: Mapping[str, float]
) -> list[int]:
    return [
        i
        for i, (name, value, (lower, upper)) in enumerate(
            zip(descriptor["parameter_names"], theta, descriptor["parameter_bounds"], strict=True)
        )
        if name in fixed
        or (lower is not None and value == lower)
        or (upper is not None and value == upper)
    ]
