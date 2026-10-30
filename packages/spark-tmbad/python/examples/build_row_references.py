"""Create independent row-model references with optional installed SciPy."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from numerical_oracles import finite_difference_hessian


def sigmoid(value):
    exponential = math.exp(-abs(value))
    return 1 / (1 + exponential) if value >= 0 else exponential / (1 + exponential)


def reference(model_id, theta, rows):
    from scipy.special import digamma, gammaln

    loss, gradient = 0.0, [0.0] * len(theta)
    for row in rows:
        if model_id in ("normal", "linear_gaussian", "quadratic_gaussian", "saturating_growth"):
            if model_id == "normal":
                mean, derivatives, y = theta[0], [1.0], row[0]
            elif model_id == "saturating_growth":
                time, y = row
                amplitude, rate = math.exp(theta[1]), math.exp(theta[2])
                decay = math.exp(-rate * time)
                mean = theta[0] + amplitude * (-math.expm1(-rate * time))
                derivatives = [
                    1.0,
                    amplitude * (-math.expm1(-rate * time)),
                    amplitude * rate * time * decay,
                ]
            else:
                x, y = row
                design = x if model_id == "linear_gaussian" else x * x
                mean, derivatives = theta[0] + theta[1] * design, [1.0, design]
            sigma2, residual = math.exp(2 * theta[-1]), y - mean
            loss += theta[-1] + 0.5 * math.log(2 * math.pi) + 0.5 * residual * residual / sigma2
            partial = [-residual / sigma2 * derivative for derivative in derivatives] + [
                1 - residual * residual / sigma2
            ]
        elif model_id == "bernoulli_logistic":
            x, y = row
            eta = theta[0] + theta[1] * x
            signed = -eta if y else eta
            loss += max(signed, 0) + math.log1p(math.exp(-abs(signed)))
            score = -sigmoid(-eta) if y else sigmoid(eta)
            partial = [score, score * x]
        else:
            if model_id == "gamma_regression":
                x, y = row
                exposure = 1.0
            else:
                x, exposure, y = row
            log_mu = theta[0] + theta[1] * x + math.log(exposure)
            mu = math.exp(log_mu)
            if model_id == "poisson_exposure":
                loss += mu - y * log_mu + math.lgamma(y + 1)
                partial = [mu - y, (mu - y) * x]
            else:
                shape = math.exp(theta[2])
                if model_id == "negative_binomial2":
                    loss += (
                        float(gammaln(shape) + gammaln(y + 1) - gammaln(shape + y))
                        + shape * math.log1p(mu / shape)
                        + y * math.log1p(shape / mu)
                    )
                    score = shape * (mu - y) / (shape + mu)
                    scale_score = shape * (
                        float(digamma(shape) - digamma(shape + y))
                        + math.log1p(mu / shape)
                        + (y - mu) / (shape + mu)
                    )
                else:
                    loss += (
                        float(gammaln(shape))
                        - shape * math.log(shape)
                        + shape * log_mu
                        - (shape - 1) * math.log(y)
                        + shape * y / mu
                    )
                    score = shape * (1 - y / mu)
                    scale_score = shape * (
                        float(digamma(shape)) - math.log(shape) - 1 + log_mu - math.log(y) + y / mu
                    )
                partial = [score, score * x, scale_score]
        gradient = [total + value for total, value in zip(gradient, partial, strict=True)]
    return {"loss": loss, "gradient": gradient}


def future_reference(model_id, theta, rows):
    result = []
    for row in rows:
        if model_id == "normal":
            result.append([theta[0], math.exp(theta[1])])
            continue
        if model_id in ("linear_gaussian", "quadratic_gaussian"):
            design = row[0] if model_id == "linear_gaussian" else row[0] ** 2
            mean, variance = theta[0] + theta[1] * design, math.exp(2 * theta[2])
        elif model_id == "saturating_growth":
            mean = theta[0] + math.exp(theta[1]) * (-math.expm1(-math.exp(theta[2]) * row[0]))
            variance = math.exp(2 * theta[3])
        elif model_id == "bernoulli_logistic":
            eta = theta[0] + theta[1] * row[0]
            mean, variance = sigmoid(eta), sigmoid(eta) * sigmoid(-eta)
        else:
            mean = math.exp(theta[0] + theta[1] * row[0]) * (row[1] if len(row) == 2 else 1)
            variance = mean if model_id == "poisson_exposure" else mean * mean / math.exp(theta[2])
            if model_id == "negative_binomial2":
                variance += mean
        result.append([mean, variance, math.sqrt(variance)])
    return result


def build():
    cases = []

    def add(model_id, theta, rows, future, *, tiny=False):
        expected = reference(model_id, theta, rows)
        expected["hessians"] = [
            finite_difference_hessian(
                lambda point: reference(model_id, point, rows)["gradient"], theta, step
            )
            for step in (1e-4, 2e-5)
        ]
        cases.append(
            {
                "model_id": model_id,
                "theta": theta,
                "rows": rows,
                "future": future,
                "expected": expected,
                "future_expected": future_reference(model_id, theta, future),
                "tiny_positive_loss": tiny,
            }
        )

    add("normal", [0.2, -0.4], [[1.2], [-0.3], [2.4]], [[], []])
    for model_id in ("linear_gaussian", "quadratic_gaussian"):
        add(model_id, [0.2, -0.4, -0.3], [[-1, 1.2], [0.3, -0.2], [1.1, 2.3]], [[-0.5], [0.8]])
    add(
        "saturating_growth",
        [0.1, math.log(2.0), math.log(0.4), -0.5],
        [[0, 0.3], [0.2, 0.7], [2, 1.5], [8, 2.3]],
        [[0], [0.5], [9]],
    )
    add(
        "poisson_exposure",
        [0.2, -0.3],
        [[-1, 0.2, 0], [0.4, 2.0, 3], [1, 5, 7]],
        [[-0.5, 0.75], [0.8, 2.0]],
    )
    add("bernoulli_logistic", [-0.2, 0.9], [[-1, 0], [0.2, 1], [1.5, 0]], [[-0.5], [0.8]])
    add("bernoulli_logistic", [40, 0], [[0, 1]], [[0]], tiny=True)
    add("bernoulli_logistic", [-40, 0], [[0, 0]], [[0]], tiny=True)
    for log_shape in (-4.0, math.log(2.5), 6.0):
        for count in (0, 64, 65, 1_000_000):
            add(
                "negative_binomial2",
                [0.2, -0.3, log_shape],
                [[-0.5, 0.2, count], [0.7, 2.0, count]],
                [[-0.5, 0.75], [0.8, 2.0]],
            )
        add(
            "negative_binomial2",
            [math.log(1000), 0.0, log_shape],
            [[0, 1000, 1_000_000]],
            [[0, 1000]],
        )
        add("negative_binomial2", [-12, 0, log_shape], [[0, 1e-6, 0]], [[0, 1e-6]], tiny=True)
        for observed in (1e-6, 1.0, 1e6):
            add(
                "gamma_regression",
                [-0.2, 0.4, log_shape],
                [[-0.5, observed], [0.7, observed * 1.2]],
                [[-0.5], [0.8]],
            )
    return cases


def main():
    import scipy

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "kind": "spark-tmbad-independent-row-references",
        "scipy_version": scipy.__version__,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": (
            "Independent analytic gradients plus SciPy distribution "
            "normalization; finite differences only in test Hessian "
            "references"
        ),
        "cases": build(),
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
