"""Exact rational active-set references for tiny convex named-penalty problems.

This does not implement or execute the proposed proximal iteration. It enumerates
sign/box active sets and solves their linear KKT equations with Fraction arithmetic.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import struct
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def matrix(values):
    return [[F(str(value)) for value in row] for row in values]


def vector(values):
    return [F(str(value)) for value in values]


def solve(a, b):
    if not b:
        return []
    rows = [list(row) + [value] for row, value in zip(a, b, strict=True)]
    n = len(b)
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None:
            raise ValueError("Singular active-set linear system")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for i in range(n):
            if i != column:
                factor = rows[i][column]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[column], strict=True)]
    return [row[-1] for row in rows]


def kkt(point, gradient, strengths, lower, upper):
    residual = []
    for x, g, strength, lo, hi in zip(point, gradient, strengths, lower, upper, strict=True):
        if lo is not None and lo == hi:
            residual.append(F(0))
            continue
        a, b = (
            (g - strength, g + strength) if x == 0 else (g + (1 if x > 0 else -1) * strength,) * 2
        )
        if lo is not None and x == lo:
            value = max(F(0), -b)
        elif hi is not None and x == hi:
            value = max(F(0), a)
        else:
            value = a if a > 0 else -b if b < 0 else F(0)
        residual.append(value)
    return residual


def assert_positive_definite(a):
    if any(a[i][j] != a[j][i] for i in range(len(a)) for j in range(len(a))):
        raise ValueError("Quadratic matrix must be symmetric")
    schur = [list(row) for row in a]
    for k in range(len(a)):
        pivot = schur[k][k]
        if pivot <= 0:
            raise ValueError("Quadratic matrix is not exactly positive definite")
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                schur[i][j] -= schur[i][k] * schur[k][j] / pivot


def active_set_reference(case):
    names = case["names"]
    a, b = matrix(case["matrix"]), vector(case["linear"])
    assert_positive_definite(a)
    lower = [None if v is None else F(str(v)) for v in case["lower"]]
    upper = [None if v is None else F(str(v)) for v in case["upper"]]
    for name, term in case["gaussian"].items():
        i = names.index(name)
        precision, center = F(str(term["precision"])), F(str(term["mean"]))
        a[i][i] += precision
        b[i] += precision * center
    strengths = [F(str(case["l1"].get(name, 0))) for name in names]
    for name, value in case["fixed"].items():
        i = names.index(name)
        lower[i] = upper[i] = F(str(value))
    choices = []
    for i in range(len(names)):
        if lower[i] is not None and lower[i] == upper[i]:
            choices.append([("fixed", lower[i])])
            continue
        states = [("free", None)] if strengths[i] == 0 else [("positive", None), ("negative", None)]
        if (lower[i] is None or lower[i] <= 0) and (upper[i] is None or upper[i] >= 0):
            states.append(("zero", F(0)))
        if lower[i] is not None:
            states.append(("lower", lower[i]))
        if upper[i] is not None:
            states.append(("upper", upper[i]))
        choices.append(states)
    accepted = set()
    for state in itertools.product(*choices):
        free = [i for i, item in enumerate(state) if item[1] is None]
        held = [i for i in range(len(names)) if i not in free]
        point = [item[1] for item in state]
        rhs = []
        for i in free:
            direction = 1 if state[i][0] == "positive" else -1 if state[i][0] == "negative" else 0
            rhs.append(b[i] - sum(a[i][j] * point[j] for j in held) - strengths[i] * direction)
        values = solve([[a[i][j] for j in free] for i in free], rhs)
        for i, value in zip(free, values, strict=True):
            point[i] = value
        if any(
            (lower[i] is not None and point[i] < lower[i])
            or (upper[i] is not None and point[i] > upper[i])
            or (state[i][0] == "positive" and point[i] <= 0)
            or (state[i][0] == "negative" and point[i] >= 0)
            for i in range(len(names))
        ):
            continue
        gradient = [
            sum(a[i][j] * point[j] for j in range(len(names))) - b[i] for i in range(len(names))
        ]
        if max(kkt(point, gradient, strengths, lower, upper)) == 0:
            accepted.add(tuple(point))
    if len(accepted) != 1:
        raise AssertionError("Expected a unique exactly certified convex solution")
    point = next(iter(accepted))
    return {
        "rational_parameters": [str(value) for value in point],
        "parameters": [float(value) for value in point],
        "raw_kkt": 0.0,
        "free_parameter_count": sum(
            lo is None or lo != hi for lo, hi in zip(lower, upper, strict=True)
        ),
    }


def target_digest(case):
    data = bytearray()

    def text(value):
        raw = value.encode("utf-8")
        data.extend(struct.pack(">i", len(raw)))
        data.extend(raw)

    def number(value):
        value = float(value)
        data.extend(struct.pack(">d", 0.0 if value == 0 else value))

    for value in [
        "spark-tmbad-named-target-v1",
        "a" * 64,
        "native_optimizer_parameters",
        "d_selected_native_optimizer_coordinates",
        "summed_likelihood_target",
        "none_penalty_only",
    ]:
        text(value)
    data.extend(struct.pack(">i", len(case["names"])))
    for i, name in enumerate(case["names"]):
        text(name)
        for bound in [case["lower"][i], case["upper"][i]]:
            data.extend(struct.pack(">?", bound is not None))
            if bound is not None:
                number(bound)
        prior = case["gaussian"].get(name)
        data.extend(struct.pack(">?", prior is not None))
        if prior:
            number(prior["mean"])
            number(prior["precision"])
        number(case["l1"].get(name, 0))
        data.extend(struct.pack(">?", name in case["fixed"]))
        if name in case["fixed"]:
            number(case["fixed"][name])
    return hashlib.sha256(data).hexdigest()


def cases():
    values = [
        {
            "id": "orthogonal_lasso",
            "names": ["intercept", "slope", "nuisance"],
            "matrix": [[20, 0, 0], [0, 20, 0], [0, 0, 20]],
            "linear": [40, 16, 0.6],
            "l1": {"slope": 2, "nuisance": 2},
            "weight": 20,
        },
        {
            "id": "correlated_prior_l1",
            "names": ["intercept", "slope", "nuisance"],
            "matrix": [[4, 1, 0], [1, 3, 0.25], [0, 0.25, 2]],
            "linear": [8, 3, 0.1],
            "gaussian": {"slope": {"mean": 0.6, "precision": 2}},
            "l1": {"nuisance": 0.8},
            "weight": 7,
        },
        {
            "id": "fixed_nuisance",
            "names": ["intercept", "slope", "nuisance"],
            "matrix": [[5, 2, 1], [2, 4, 1], [1, 1, 3]],
            "linear": [7, 3, 4],
            "gaussian": {"slope": {"mean": -0.2, "precision": 1.5}},
            "l1": {"intercept": 0.4},
            "fixed": {"nuisance": 0.8},
            "weight": 11,
        },
        {
            "id": "positive_box_excludes_zero",
            "names": ["coefficient"],
            "matrix": [[1]],
            "linear": [-3],
            "l1": {"coefficient": 2},
            "lower": [1],
            "upper": [4],
            "initial": [2],
            "weight": 5,
        },
        {
            "id": "negative_upper_box",
            "names": ["coefficient"],
            "matrix": [[1]],
            "linear": [3],
            "l1": {"coefficient": 1},
            "lower": [-4],
            "upper": [-1],
            "initial": [-2],
            "weight": 5,
        },
        {
            "id": "all_fixed",
            "names": ["intercept", "slope"],
            "matrix": [[2, 1], [1, 3]],
            "linear": [100, -50],
            "gaussian": {"intercept": {"mean": -0.5, "precision": 0.2}},
            "l1": {"slope": 0.7},
            "fixed": {"intercept": 2, "slope": 3},
            "weight": 9,
        },
        {
            "id": "nonzero_gaussian_center",
            "names": ["intercept", "slope"],
            "matrix": [[6, 2], [2, 5]],
            "linear": [5, -1],
            "gaussian": {"slope": {"mean": 1.4, "precision": 3}},
            "weight": 8,
        },
        {
            "id": "unequal_weight_mass",
            "names": ["first", "second"],
            "matrix": [[0.5, 0], [0, 2]],
            "linear": [1, 4],
            "gaussian": {"first": {"mean": -0.1, "precision": 0.3}},
            "l1": {"first": 0.2, "second": 0.7},
            "weight": 200,
        },
        {
            "id": "exact_threshold_zero",
            "names": ["coefficient"],
            "matrix": [[1]],
            "linear": [1],
            "l1": {"coefficient": 1},
            "weight": 3,
        },
    ]
    for case in values:
        size = len(case["names"])
        for name, default in [
            ("lower", [None] * size),
            ("upper", [None] * size),
            ("initial", [0.0] * size),
            ("gaussian", {}),
            ("l1", {}),
            ("fixed", {}),
        ]:
            case.setdefault(name, default)
        case["constant"] = 0.0
        case["expected"] = active_set_reference(case)
        point = [F(value) for value in case["expected"]["rational_parameters"]]
        a, b = matrix(case["matrix"]), vector(case["linear"])
        raw_loss = sum(
            point[i] * a[i][j] * point[j] for i in range(size) for j in range(size)
        ) / 2 - sum(x * y for x, y in zip(point, b, strict=True))
        raw_gradient = [sum(a[i][j] * point[j] for j in range(size)) - b[i] for i in range(size)]
        prior_quadratic, prior_normalizer = F(0), 0.0
        prior_gradient = [F(0)] * size
        for name, term in case["gaussian"].items():
            i = case["names"].index(name)
            precision, center = F(str(term["precision"])), F(str(term["mean"]))
            prior_quadratic += precision * (point[i] - center) ** 2 / 2
            prior_gradient[i] = precision * (point[i] - center)
            prior_normalizer += 0.5 * (math.log(2 * math.pi) - math.log(float(precision)))
        l1_value = sum(
            F(str(case["l1"].get(name, 0))) * abs(point[i]) for i, name in enumerate(case["names"])
        )
        composite = float(raw_loss + prior_quadratic + l1_value) + prior_normalizer
        case["expected"].update(
            raw_data_value=float(raw_loss),
            gaussian_quadratic=float(prior_quadratic),
            gaussian_normalizer=prior_normalizer,
            raw_l1_value=float(l1_value),
            composite_sum=composite,
            composite_weighted_mean=composite / case["weight"],
            raw_data_gradient=[float(x) for x in raw_gradient],
            raw_smooth_gradient=[
                float(x + y) for x, y in zip(raw_gradient, prior_gradient, strict=True)
            ],
        )
        case["expected_target_digest"] = target_digest(case)
    return values


def main():
    payload = {
        "schema_version": 1,
        "scope": (
            "independent exact rational KKT references for nine small convex quadratics; "
            "not Scala/native/Spark execution"
        ),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cases": cases(),
    }
    (ROOT / "oracles/convex-targets.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "exactly_certified_cases": len(payload["cases"]),
                "scala_compiled": False,
                "scala_executed": False,
            }
        )
    )


if __name__ == "__main__":
    main()
