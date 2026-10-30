"""Original bounded simulation fixtures and Monte Carlo summaries (standard library)."""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

Z95 = 1.959963984540054


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def uniform(seed: int, *key: str | int) -> float:
    """Independent keyed 52-bit uniforms, strictly between zero and one."""
    raw = hashlib.sha256(canonical([seed, *key])).digest()
    integer = int.from_bytes(raw[:8], "big") >> 12
    return (integer + 0.5) / 2**52


def normal(seed: int, *key: str | int) -> float:
    return math.sqrt(-2.0 * math.log(uniform(seed, *key, "radius"))) * math.cos(
        2.0 * math.pi * uniform(seed, *key, "angle")
    )


def bounded_json(path: Path, limit: int = 4 * 1024 * 1024) -> dict[str, Any]:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("Study input exceeds its declared byte bound")
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("Study input must be a JSON object")
    canonical(result)
    return result


def mean(values: list[float]) -> float:
    if not values or not all(math.isfinite(x) for x in values):
        raise ValueError("A mean requires nonempty finite observations")
    return math.fsum(values) / len(values)


def variance(values: list[float]) -> float:
    center = mean(values)
    return math.fsum((x - center) ** 2 for x in values) / len(values)


def wilson(successes: int, count: int) -> dict[str, float | int]:
    if (
        type(successes) is not int
        or type(count) is not int
        or not 0 <= successes <= count
        or count < 1
    ):
        raise ValueError("Invalid binomial summary counts")
    p = successes / count
    denominator = 1 + Z95**2 / count
    center = (p + Z95**2 / (2 * count)) / denominator
    half = Z95 * math.sqrt(p * (1 - p) / count + Z95**2 / (4 * count**2)) / denominator
    return {
        "successes": successes,
        "count": count,
        "estimate": p,
        "mcse": math.sqrt(p * (1 - p) / count),
        "wilson95_lower": max(0.0, center - half),
        "wilson95_upper": min(1.0, center + half),
    }


def scalar_summary(values: list[float]) -> dict[str, float | int | None]:
    center = mean(values)
    mcse = statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None
    return {"count": len(values), "mean": center, "mcse": mcse}


def paired_summary(left: list[float], right: list[float]) -> dict[str, float | int | None]:
    if len(left) != len(right):
        raise ValueError("Paired Monte Carlo methods must share the same replication set")
    return scalar_summary([a - b for a, b in zip(left, right, strict=True)])


def aggregate(records: list[dict[str, Any]], truth: list[float]) -> dict[str, Any]:
    if not records:
        raise ValueError("A study cannot summarize zero attempted replications")
    if not truth or not all(math.isfinite(x) for x in truth):
        raise ValueError("Study truth must be nonempty and finite")
    if any(record.get("status") not in {"passed", "failed"} for record in records):
        raise ValueError("Only actually attempted passed/failed records can be aggregated")
    passed = [record for record in records if record.get("status") == "passed"]
    result: dict[str, Any] = {
        "attempted": len(records),
        "successful": len(passed),
        "failure_fraction": wilson(len(records) - len(passed), len(records)),
        "estimate_scope": "conditional on successful fits; failures retained separately",
    }
    if passed:
        if any(len(record["parameters"]) != len(truth) for record in passed):
            raise ValueError("Parameter dimensions differ across study replications")
        estimates = []
        for j, actual in enumerate(truth):
            errors = [record["parameters"][j] - actual for record in passed]
            squared = [x * x for x in errors]
            mse = scalar_summary(squared)
            estimates.append(
                {
                    "parameter_index": j,
                    "truth": actual,
                    "bias": scalar_summary(errors),
                    "mse": mse,
                    "rmse": math.sqrt(float(mse["mean"])),
                }
            )
        result["parameters"] = estimates
    return result


def gaussian_nll(y: float, location: float, sd: float) -> float:
    if sd <= 0 or not all(math.isfinite(x) for x in (y, location, sd)):
        raise ValueError("Gaussian density arguments must be finite with positive scale")
    return math.log(sd) + 0.5 * math.log(2 * math.pi) + 0.5 * ((y - location) / sd) ** 2


def normal_posterior(
    observations: list[float], sigma: float, prior_mean: float, prior_sd: float
) -> dict[str, float]:
    if (
        sigma <= 0
        or prior_sd <= 0
        or not observations
        or not all(math.isfinite(x) for x in [sigma, prior_mean, prior_sd, *observations])
    ):
        raise ValueError("Normal posterior needs data and positive known/prior scales")
    precision = len(observations) / sigma**2 + 1 / prior_sd**2
    posterior_mean = (math.fsum(observations) / sigma**2 + prior_mean / prior_sd**2) / precision
    return {
        "mean": posterior_mean,
        "mode": posterior_mean,
        "variance": 1 / precision,
        "predictive_variance": sigma**2 + 1 / precision,
    }


def gamma_poisson_posterior(
    counts: list[int], exposure: list[float], shape: float, rate: float
) -> dict[str, Any]:
    if (
        len(counts) != len(exposure)
        or not counts
        or shape <= 0
        or rate <= 0
        or not math.isfinite(shape)
        or not math.isfinite(rate)
    ):
        raise ValueError("Invalid conjugate Gamma-Poisson inputs")
    if any(type(y) is not int or y < 0 for y in counts) or any(
        type(e) not in (int, float) or not math.isfinite(e) or e <= 0 for e in exposure
    ):
        raise ValueError("Counts must be nonnegative integers and exposures positive")
    a, b = shape + sum(counts), rate + math.fsum(exposure)
    return {
        "shape": a,
        "rate": b,
        "mean": a / b,
        "variance": a / b**2,
        "natural_coordinate_interior_map": (a - 1) / b if a > 1 else None,
        "natural_coordinate_boundary_supremum": 0.0 if a <= 1 else None,
        "log_coordinate_map_mapped_to_rate": a / b,
        "unit_exposure_predictive_mean": a / b,
        "unit_exposure_predictive_variance": a / b + a / b**2,
    }


def orthogonal_estimate(
    design: list[list[float]],
    response: list[float],
    sigma: float,
    strength: float,
    penalty: str,
    penalized: list[bool],
) -> dict[str, Any]:
    """Exact closed-form reference, not a production distributed lasso optimizer."""
    if (
        not design
        or len(design) != len(response)
        or sigma <= 0
        or not math.isfinite(sigma)
        or strength < 0
        or not math.isfinite(strength)
        or penalty not in ("none", "ridge", "lasso")
    ):
        raise ValueError("Invalid orthogonal regression problem")
    p = len(design[0])
    n = len(design)
    if p != len(penalized) or not 1 <= p <= 16 or any(len(row) != p for row in design):
        raise ValueError("Orthogonal design shape differs")
    if (
        any(type(x) is not bool for x in penalized)
        or not all(math.isfinite(x) for row in design for x in row)
        or not all(math.isfinite(x) for x in response)
    ):
        raise ValueError("Design/response must be finite and penalty selectors boolean")
    for j in range(p):
        for k in range(p):
            target = n if j == k else 0
            if abs(math.fsum(row[j] * row[k] for row in design) - target) > 1e-10:
                raise ValueError("This reference requires X'X=nI, not an arbitrary design")
    cross = [
        math.fsum(row[j] * y for row, y in zip(design, response, strict=True)) for j in range(p)
    ]
    beta = []
    for j in range(p):
        unpenalized = cross[j] / n
        if not penalized[j] or penalty == "none":
            beta.append(unpenalized)
        elif penalty == "ridge":
            beta.append(cross[j] / (n + strength * sigma**2))
        else:
            threshold = strength * sigma**2 / n
            beta.append(math.copysign(max(abs(unpenalized) - threshold, 0), unpenalized))
    gradient = [(n * b - c) / sigma**2 for b, c in zip(beta, cross, strict=True)]
    residual = []
    for j, (b, g) in enumerate(zip(beta, gradient, strict=True)):
        if not penalized[j] or penalty == "none":
            residual.append(abs(g))
        elif penalty == "ridge":
            residual.append(abs(g + strength * b))
        elif b == 0:
            residual.append(max(abs(g) - strength, 0))
        else:
            residual.append(abs(g + strength * math.copysign(1, b)))
    fitted = [math.fsum(x * b for x, b in zip(row, beta, strict=True)) for row in design]
    likelihood = math.fsum(gaussian_nll(y, m, sigma) for y, m in zip(response, fitted, strict=True))
    regularizer = math.fsum(
        (0.5 * strength * b * b if penalty == "ridge" else strength * abs(b))
        for j, b in enumerate(beta)
        if penalized[j] and penalty != "none"
    )
    return {
        "parameters": beta,
        "data_nll": likelihood,
        "penalty_value": regularizer,
        "objective": likelihood + regularizer,
        "kkt_residual_inf": max(residual),
        "penalty": penalty,
        "penalized_coordinates": penalized,
    }


def objective(
    case: dict[str, Any], theta: list[float], strength: float = 0.0
) -> tuple[float, list[float]]:
    """Independent analytic value/score on an already retained small synthetic fixture."""
    if (
        not theta
        or not all(math.isfinite(x) for x in theta)
        or not math.isfinite(strength)
        or strength < 0
    ):
        raise ValueError("Invalid reference objective parameters")
    rows = case["training"]
    kind = case["case"]
    expected = {
        "normal_mle": 2,
        "linear_all_coordinate_map": 3,
        "nonlinear_growth": 4,
        "random_intercept": 3,
    }
    if kind not in expected or len(theta) != expected[kind] or not rows:
        raise ValueError("Unsupported reference objective or dimension")
    value = 0.0
    gradient = [0.0] * len(theta)
    if kind == "random_intercept":
        groups: dict[str, list[float]] = {}
        for row in rows:
            groups.setdefault(row["unit"], []).append(row["y"])
        beta, logs, logt = theta
        s, t = math.exp(2 * logs), math.exp(2 * logt)
        for values in groups.values():
            n = len(values)
            average = mean(values)
            sse = math.fsum((y - average) ** 2 for y in values)
            shift = average - beta
            v = s + n * t
            value += 0.5 * (
                n * math.log(2 * math.pi)
                + (n - 1) * 2 * logs
                + math.log(v)
                + sse / s
                + n * shift * shift / v
            )
            gradient[0] += -n * shift / v
            gradient[1] += (n - 1) + s / v - sse / s - n * shift * shift * s / v**2
            gradient[2] += n * t / v - n * n * shift * shift * t / v**2
    else:
        if kind == "nonlinear_growth" and strength:
            raise ValueError("The growth coordinate map preserves likelihood, not isotropic L2")
        log_sigma = theta[-1]
        inverse = math.exp(-2 * log_sigma)
        for row in rows:
            weight = row.get("weight", 1.0)
            if kind == "normal_mle":
                location = theta[0]
                derivatives = [1.0]
            elif kind == "linear_all_coordinate_map":
                location = theta[0] + theta[1] * row["x"]
                derivatives = [1.0, row["x"]]
            else:
                amplitude, rate = math.exp(theta[1]), math.exp(theta[2])
                time = row["time"]
                growth = -amplitude * math.expm1(-rate * time)
                location = theta[0] + growth
                derivatives = [1.0, growth, amplitude * rate * time * math.exp(-rate * time)]
            residual = location - row["y"]
            value += weight * (
                log_sigma + 0.5 * math.log(2 * math.pi) + 0.5 * residual * residual * inverse
            )
            for j, derivative in enumerate(derivatives):
                gradient[j] += weight * residual * inverse * derivative
            gradient[-1] += weight * (1 - residual * residual * inverse)
    if strength:
        value += 0.5 * strength * math.fsum(x * x for x in theta)
        gradient = [g + strength * x for g, x in zip(gradient, theta, strict=True)]
    if not math.isfinite(value) or not all(math.isfinite(x) for x in gradient):
        raise ValueError("Reference objective is nonfinite")
    return value, gradient


def prediction_reference(case: dict[str, Any], theta: list[float]) -> list[dict[str, Any]]:
    """Explicit plug-in moments, not a claim that every backend exposes these targets."""
    result = []
    kind = case["case"]
    for row in case["future"]:
        if kind == "normal_mle":
            location = theta[0]
            var = math.exp(2 * theta[1])
        elif kind == "linear_all_coordinate_map":
            location = theta[0] + theta[1] * row["x"]
            var = math.exp(2 * theta[2])
        elif kind == "nonlinear_growth":
            location = theta[0] - math.exp(theta[1]) * math.expm1(-math.exp(theta[2]) * row["time"])
            var = math.exp(2 * theta[3])
        elif kind == "random_intercept":
            s, t = math.exp(2 * theta[1]), math.exp(2 * theta[2])
            location = theta[0]
            var = s + t
            if row["cohort"] == "known":
                past = [item["y"] for item in case["training"] if item["unit"] == row["unit"]]
                if not past:
                    raise ValueError("Known-group reference requires its observed history")
                n = len(past)
                v = 1 / (1 / t + n / s)
                location += v * n * (mean(past) - theta[0]) / s
                var = s + v
        else:
            raise ValueError("Unknown prediction reference")
        result.append(
            {
                "row_id": row["row_id"],
                "mean": location,
                "variance": var,
                "cohort": row.get("cohort", "future"),
            }
        )
    return result


def forecast_metrics(case: dict[str, Any], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    index = {item["row_id"]: item for item in predictions}
    if len(index) != len(predictions) or set(index) != {row["row_id"] for row in case["future"]}:
        raise ValueError("Future prediction identity coverage differs")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in case["future"]:
        p = index[row["row_id"]]
        var = p["variance"]
        if not math.isfinite(var) or var <= 0:
            raise ValueError("Predictive variance must be positive")
        error = row["y"] - p["mean"]
        covered = abs(error) <= Z95 * math.sqrt(var)
        grouped.setdefault(row.get("cohort", "future"), []).append(
            {
                "squared_error": error * error,
                "nll": gaussian_nll(row["y"], p["mean"], math.sqrt(var)),
                "covered": covered,
                "unit": row.get("unit", "whole_future_path"),
            }
        )
    output = {}
    for cohort, records in grouped.items():
        paths: dict[str, list[bool]] = {}
        for item in records:
            paths.setdefault(item["unit"], []).append(item["covered"])
        output[cohort] = {
            "rows": len(records),
            "mse": mean([x["squared_error"] for x in records]),
            "mean_marginal_nll": mean([x["nll"] for x in records]),
            "pointwise_coverage": sum(x["covered"] for x in records) / len(records),
            "unadjusted_pointwise_bands_joint_coverage": sum(all(v) for v in paths.values())
            / len(paths),
            "paths": len(paths),
            "uncertainty": "plug-in population parameters; no parameter uncertainty",
        }
    return output
