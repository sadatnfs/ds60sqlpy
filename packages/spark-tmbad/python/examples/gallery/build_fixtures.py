"""Generate public synthetic fixtures shared by the Python and Scala galleries."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


def poisson(random_source, mean):
    product, count, threshold = 1.0, 0, math.exp(-mean)
    while product > threshold:
        product *= random_source.random()
        count += 1
    return count - 1


def portable(value):
    """Fix public fixture precision above insignificant cross-platform libm roundoff."""
    if isinstance(value, float):
        return float(format(value, ".12g"))
    if isinstance(value, dict):
        return {key: portable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable(item) for item in value]
    return value


def operation(target, fields, rows, history=None, order=()):
    return {
        "target": target,
        "fields": list(fields),
        "rows": rows,
        "history_rows": [] if history is None else history,
        "order_columns": list(order),
    }


def case(
    model_id,
    fields,
    initial,
    generating,
    rows,
    *,
    groups=(),
    order=(),
    predictions=None,
    forecasts=None,
):
    return {
        "model_id": model_id,
        "fit_fields": fields,
        "initial_parameters": initial,
        "generating_parameters": generating,
        "seed": 1789,
        "id_columns": ["row_id"],
        "group_columns": list(groups),
        "order_columns": list(order),
        "training_rows": rows,
        "prediction_cases": predictions or [],
        "forecast_cases": forecasts or [],
        "fit_options": {
            "max_iterations": 200,
            "gradient_tolerance": 1e-5,
            "function_tolerance": 0.0,
            "max_line_search": 40,
            "batch_rows": 64,
        },
    }


def build():
    rng = random.Random(1789)
    cases = {}
    row_models = [
        "normal",
        "linear_gaussian",
        "quadratic_gaussian",
        "poisson_exposure",
        "bernoulli_logistic",
        "negative_binomial2",
        "gamma_regression",
        "saturating_growth",
    ]
    for model_id in row_models:
        rows = []
        for index in range(160 if model_id == "bernoulli_logistic" else 128):
            x, exposure, time = rng.uniform(-1.5, 1.5), rng.uniform(0.7, 2.0), index / 16
            row = {"row_id": index}
            if model_id == "normal":
                row["y"] = 1.5 + 0.7 * rng.gauss(0, 1)
            elif model_id == "linear_gaussian":
                row.update(x=x, y=0.6 + 1.2 * x + 0.4 * rng.gauss(0, 1))
            elif model_id == "quadratic_gaussian":
                row.update(x=x, y=1.0 + 0.7 * x * x + 0.3 * rng.gauss(0, 1))
            elif model_id == "poisson_exposure":
                row.update(
                    x=x, exposure=exposure, y=poisson(rng, exposure * math.exp(0.2 + 0.6 * x))
                )
            elif model_id == "bernoulli_logistic":
                probability = 1 / (1 + math.exp(-(-0.2 + 0.9 * x)))
                row.update(x=x, y=int(rng.random() < probability))
            elif model_id == "negative_binomial2":
                mean = exposure * math.exp(0.2 + 0.6 * x)
                count = poisson(rng, rng.gammavariate(3.0, mean / 3.0))
                if count > 64:
                    raise AssertionError("Known fixture exceeded the declared count support")
                row.update(x=x, exposure=exposure, y=count)
            elif model_id == "gamma_regression":
                mean = math.exp(0.3 + 0.5 * x)
                row.update(x=x, y=rng.gammavariate(4.0, mean / 4.0))
            else:
                row.update(
                    time=time, y=0.4 + 2.5 * (-math.expm1(-0.55 * time)) + 0.2 * rng.gauss(0, 1)
                )
            rows.append(row)
        choices = {
            "normal": (
                ["y"],
                [1.0, 0.0],
                [1.5, math.log(0.7)],
                [],
                [{"row_id": 1000}, {"row_id": 1001}],
            ),
            "linear_gaussian": (
                ["x", "y"],
                [0.3, 0.5, math.log(0.8)],
                [0.6, 1.2, math.log(0.4)],
                ["x"],
                [{"row_id": 1000, "x": -0.5}, {"row_id": 1001, "x": 1.0}],
            ),
            "quadratic_gaussian": (
                ["x", "y"],
                [0.5, 0.3, math.log(0.6)],
                [1.0, 0.7, math.log(0.3)],
                ["x"],
                [{"row_id": 1000, "x": -0.5}, {"row_id": 1001, "x": 1.0}],
            ),
            "poisson_exposure": (
                ["x", "exposure", "y"],
                [0.0, 0.3],
                [0.2, 0.6],
                ["x", "exposure"],
                [
                    {"row_id": 1000, "x": -0.5, "exposure": 1.0},
                    {"row_id": 1001, "x": 1.0, "exposure": 1.5},
                ],
            ),
            "bernoulli_logistic": (
                ["x", "y"],
                [0.0, 0.3],
                [-0.2, 0.9],
                ["x"],
                [{"row_id": 1000, "x": -0.5}, {"row_id": 1001, "x": 1.0}],
            ),
            "negative_binomial2": (
                ["x", "exposure", "y"],
                [0.0, 0.3, math.log(2.0)],
                [0.2, 0.6, math.log(3.0)],
                ["x", "exposure"],
                [
                    {"row_id": 1000, "x": -0.5, "exposure": 1.0},
                    {"row_id": 1001, "x": 1.0, "exposure": 1.5},
                ],
            ),
            "gamma_regression": (
                ["x", "y"],
                [0.0, 0.2, math.log(2.0)],
                [0.3, 0.5, math.log(4.0)],
                ["x"],
                [{"row_id": 1000, "x": -0.5}, {"row_id": 1001, "x": 1.0}],
            ),
            "saturating_growth": (
                ["time", "y"],
                [0.2, math.log(2), math.log(0.4), math.log(0.4)],
                [0.4, math.log(2.5), math.log(0.55), math.log(0.2)],
                ["time"],
                [{"row_id": 1000, "time": 8.0}, {"row_id": 1001, "time": 10.0}],
            ),
        }
        fields, initial, generating, target_fields, future = choices[model_id]
        target = operation("response", target_fields, future)
        cases[model_id] = case(
            model_id, fields, initial, generating, rows, predictions=[target], forecasts=[target]
        )

    for model_id in (
        "gaussian_random_intercept",
        "gaussian_random_intercept_laplace",
        "poisson_random_intercept",
        "poisson_random_slope",
        "ar1",
        "gaussian_ar1_random_intercept",
    ):
        rows = []
        ordered = model_id in ("ar1", "gaussian_ar1_random_intercept")
        for group in range(12 if model_id == "poisson_random_slope" else 10):
            u0, u1 = 0.6 * rng.gauss(0, 1), 0.35 * rng.gauss(0, 1)
            previous = 0.35 / math.sqrt(1 - 0.55**2) * rng.gauss(0, 1)
            for index in range(20 if ordered else 8):
                row = {"row_id": len(rows), "series": f"s{group}"}
                x, exposure = (index - 3.5) / 3.5, rng.uniform(0.8, 2.0)
                if model_id.startswith("gaussian_random_intercept"):
                    row["y"] = 0.7 + u0 + 0.45 * rng.gauss(0, 1)
                elif model_id == "poisson_random_intercept":
                    row.update(exposure=exposure, y=poisson(rng, exposure * math.exp(0.2 + u0)))
                elif model_id == "poisson_random_slope":
                    row.update(
                        x=x,
                        exposure=exposure,
                        y=poisson(rng, exposure * math.exp(0.2 + 0.5 * x + u0 + u1 * x)),
                    )
                else:
                    if index:
                        previous = 0.55 * previous + 0.35 * rng.gauss(0, 1)
                    row.update(
                        time=index,
                        y=0.4
                        + previous
                        + (u0 if model_id == "gaussian_ar1_random_intercept" else 0.0),
                    )
                rows.append(row)
        history = [row for row in rows if row["series"] == "s0"]
        if model_id.startswith("gaussian_random_intercept"):
            fields, initial, truth, future_fields = (
                ["y"],
                [0.5, math.log(0.6), math.log(0.8)],
                [0.7, math.log(0.45), math.log(0.6)],
                [],
            )
            future = [{"row_id": 1000 + i, "series": "s0"} for i in range(2)]
        elif model_id == "poisson_random_intercept":
            fields, initial, truth, future_fields = (
                ["exposure", "y"],
                [0.1, math.log(0.5)],
                [0.2, math.log(0.6)],
                ["exposure"],
            )
            future = [
                {"row_id": 1000 + i, "series": "s0", "exposure": exposure}
                for i, exposure in enumerate((0.75, 1.5))
            ]
        elif model_id == "poisson_random_slope":
            fields, initial, truth, future_fields = (
                ["x", "exposure", "y"],
                [0.1, 0.3, math.log(0.5), math.log(0.3)],
                [0.2, 0.5, math.log(0.6), math.log(0.35)],
                ["x", "exposure"],
            )
            future = [
                {"row_id": 1000 + i, "series": "s0", "x": x, "exposure": exposure}
                for i, (x, exposure) in enumerate(((-0.5, 1.0), (0.8, 1.5)))
            ]
        else:
            fields, initial, truth, future_fields = (
                ["time", "y"],
                [0.3, math.atanh(0.3), math.log(0.5)],
                [0.4, math.atanh(0.55), math.log(0.35)],
                ["time"],
            )
            if model_id == "gaussian_ar1_random_intercept":
                initial += [math.log(0.5)]
                truth += [math.log(0.6)]
            future = [{"row_id": 1000 + i, "series": "s0", "time": 20 + i} for i in range(3)]
        existing_target = "conditional_history" if ordered else "existing_group"
        new_target = "stationary_new_series" if ordered else "new_group"
        existing = operation(
            existing_target, future_fields, future, history, ["time"] if ordered else []
        )
        unseen = operation(
            new_target,
            future_fields,
            [{**row, "row_id": row["row_id"] + 1000, "series": "unseen"} for row in future],
            order=["time"] if ordered else [],
        )
        predictions = [existing, unseen]
        if model_id == "ar1":
            predictions = [
                operation(
                    "response", ["lag"], [{"row_id": 3000, "series": "s0", "lag": history[-1]["y"]}]
                )
            ]
        cases[model_id] = case(
            model_id,
            fields,
            initial,
            truth,
            rows,
            groups=["series"],
            order=["time"] if ordered else [],
            predictions=predictions,
            forecasts=[existing, unseen],
        )
    # These two implementations represent the same Gaussian integral. Identical
    # data isolates the exact versus generic-Laplace computation in the gallery.
    cases["gaussian_random_intercept_laplace"] = json.loads(
        json.dumps(cases["gaussian_random_intercept"])
    )
    cases["gaussian_random_intercept_laplace"]["model_id"] = "gaussian_random_intercept_laplace"
    return portable(
        {
            "schema_version": 1,
            "kind": "spark-tmbad-gallery-fixtures",
            "cases": cases,
            "scope": "Small public synthetic data; generating parameters are not exact finite-sample MLEs",
        }
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = Path(__file__).with_name("fixtures.json")
    text = json.dumps(build(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check:
        if path.read_text() != text:
            raise SystemExit("Gallery fixtures differ from the deterministic generator")
    else:
        path.write_text(text)


if __name__ == "__main__":
    main()
