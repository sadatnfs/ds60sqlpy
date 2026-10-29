"""Explicit optional SciPy driver optimization with numerical diagnostics."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from .contracts import (
    ObjectiveError,
    ObjectiveEvaluation,
    finite_number,
    finite_vector,
    parameter_digest,
)


@dataclass(frozen=True)
class OptimizationResult:
    parameters: tuple[float, ...]
    evaluation: ObjectiveEvaluation
    converged: bool
    status: int
    message: str
    iterations: int
    objective_calls: int
    gradient_inf_norm: float
    projected_gradient_inf_norm: float
    active_bounds: tuple[int, ...]
    trace: tuple[tuple[float, float], ...]


def minimize_lbfgsb(
    evaluate: Callable[[Sequence[float]], ObjectiveEvaluation],
    initial: Sequence[float],
    *,
    bounds: Sequence[tuple[float | None, float | None]] | None = None,
    max_iterations: int = 100,
    gradient_tolerance: float = 1e-7,
    function_tolerance: float = 1e-12,
) -> OptimizationResult:
    """Run a bounded number of deterministic driver evaluations.

    L-BFGS-B success alone does not establish identifiability, a global optimum
    or valid uncertainty. Return both raw and bound-projected gradient norms.
    Invalid objective values raise immediately; they are not replaced by zero
    or silently clipped into a different mathematical model.
    """
    theta = finite_vector(initial)
    if type(max_iterations) is not int or not 1 <= max_iterations <= 1000:
        raise ObjectiveError("max_iterations must be within 1..1000")
    gtol = finite_number(gradient_tolerance, "gradient tolerance")
    ftol = finite_number(function_tolerance, "function tolerance")
    if gtol <= 0 or ftol <= 0:
        raise ObjectiveError("optimizer tolerances must be positive")
    limits: list[tuple[float | None, float | None]] = []
    if bounds is not None:
        if len(bounds) != len(theta):
            raise ObjectiveError("bounds must match the parameter count")
        for value, pair in zip(theta, bounds, strict=True):
            if len(pair) != 2:
                raise ObjectiveError("each bound needs lower and upper values")
            lower = None if pair[0] is None else finite_number(pair[0], "lower bound")
            upper = None if pair[1] is None else finite_number(pair[1], "upper bound")
            if lower is not None and upper is not None and lower >= upper:
                raise ObjectiveError("each lower bound must be less than its upper bound")
            if (lower is not None and value < lower) or (upper is not None and value > upper):
                raise ObjectiveError("initial parameters must lie inside explicit bounds")
            limits.append((lower, upper))
    else:
        limits = [(None, None)] * len(theta)
    try:
        scipy = import_module("scipy.optimize")
        numpy = import_module("numpy")
    except ImportError:
        raise ObjectiveError("prepare the explicit SciPy driver environment") from None

    trace: list[tuple[float, float]] = []
    last: ObjectiveEvaluation | None = None
    calls = 0
    # Line search may evaluate more often than the number of iterations.
    call_limit = 25 * max_iterations + 1

    def objective(values: Any) -> tuple[float, Any]:
        nonlocal calls, last
        if calls >= call_limit:
            raise ObjectiveError("bounded objective evaluation budget exhausted")
        parameters = finite_vector(values)
        result = evaluate(parameters)
        if not isinstance(result, ObjectiveEvaluation):
            raise ObjectiveError("objective must return an ObjectiveEvaluation")
        if result.parameter_digest != parameter_digest(parameters):
            raise ObjectiveError("optimizer received an evaluation for stale parameters")
        value = finite_number(result.value, "optimizer objective")
        gradient = finite_vector(result.gradient, "optimizer gradient")
        if len(gradient) != len(parameters):
            raise ObjectiveError("optimizer gradient dimension mismatch")
        calls += 1
        last = result
        trace.append((value, max(abs(item) for item in gradient)))
        return value, numpy.asarray(gradient, dtype=numpy.float64)

    result = scipy.minimize(
        objective,
        numpy.asarray(theta, dtype=numpy.float64),
        jac=True,
        method="L-BFGS-B",
        bounds=limits,
        options={
            "maxiter": max_iterations,
            "maxfun": call_limit - 1,
            "maxls": 20,
            "gtol": gtol,
            "ftol": ftol,
        },
    )
    fitted = finite_vector(result.x)
    if last is None or last.parameter_digest != parameter_digest(fitted):
        objective(fitted)
    assert last is not None
    # L-BFGS-B clips active constraints to their exact float64 bounds.
    # A fixed epsilon would misclassify interior points in narrow intervals.
    active = []
    projected = []
    for index, (value, gradient, (lower, upper)) in enumerate(
        zip(fitted, last.gradient, limits, strict=True)
    ):
        at_lower = lower is not None and value == lower
        at_upper = upper is not None and value == upper
        if at_lower or at_upper:
            active.append(index)
        projected.append(
            0.0 if (at_lower and gradient > 0) or (at_upper and gradient < 0) else gradient
        )
    return OptimizationResult(
        fitted,
        last,
        bool(result.success),
        int(result.status),
        str(result.message),
        int(result.nit),
        calls,
        max(abs(value) for value in last.gradient),
        max(abs(value) for value in projected),
        tuple(active),
        tuple(trace),
    )
