# SPDX-License-Identifier: MIT
"""Independent small-fixture mathematics for native0.2 studies, not a backend."""

from __future__ import annotations

import math

from study_support import Z95, gaussian_nll, mean

FIELDS = {
    "normal": ["y"],
    "linear_gaussian": ["x", "y"],
    "student_t_regression": ["x", "y"],
    "binomial_logistic": ["x", "trials", "y"],
    "beta_binomial": ["x", "trials", "y"],
    "poisson_exposure": ["x", "exposure", "y"],
    "zero_inflated_poisson": ["x", "z", "exposure", "y"],
    "hurdle_poisson": ["x", "z", "exposure", "y"],
    "gaussian_correlated_random_slope": ["x", "y"],
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def close(actual, expected, relative=1e-7, absolute=1e-7):
    require(
        type(actual) in (int, float)
        and math.isfinite(actual)
        and math.isfinite(expected)
        and math.isclose(actual, expected, rel_tol=relative, abs_tol=absolute),
        f"Expected{expected!r}, observed{actual!r}",
    )


def probability(eta):
    e = math.exp(-abs(eta))
    return 1 / (1 + e) if eta >= 0 else e / (1 + e)


def softplus(eta):
    return max(eta, 0) + math.log1p(math.exp(-abs(eta)))


def logadd(left, right):
    return max(left, right) + math.log1p(math.exp(-abs(left - right)))


def row_nll(model, theta, row):
    """Fully normalized moderate-domain densities independently expressed with libm."""
    y = row["y"]
    if model == "normal":
        return gaussian_nll(y, theta[0], math.exp(theta[1]))
    if model == "linear_gaussian":
        return gaussian_nll(y, theta[0] + theta[1] * row["x"], math.exp(theta[2]))
    if model == "student_t_regression":
        nu = 2 + math.exp(theta[3])
        scale = math.exp(theta[2])
        residual = (y - theta[0] - theta[1] * row["x"]) / scale
        return (
            math.log(scale)
            + 0.5 * math.log(nu * math.pi)
            + math.lgamma(nu / 2)
            - math.lgamma((nu + 1) / 2)
            + 0.5 * (nu + 1) * math.log1p(residual * residual / nu)
        )
    eta = theta[0] + theta[1] * row["x"]
    if model in {"binomial_logistic", "beta_binomial"}:
        n = row["trials"]
        logchoose = math.lgamma(n + 1) - math.lgamma(y + 1) - math.lgamma(n - y + 1)
        if model == "binomial_logistic":
            return -logchoose + y * softplus(-eta) + (n - y) * softplus(eta)
        p = probability(eta)
        precision = math.exp(theta[2])
        alpha = p * precision
        beta = (1 - p) * precision

        def logbeta(a, b):
            return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)

        return -logchoose - logbeta(y + alpha, n - y + beta) + logbeta(alpha, beta)
    eta += math.log(row["exposure"])
    mu = math.exp(eta)
    base = mu - y * eta + math.lgamma(y + 1)
    if model == "poisson_exposure":
        return base
    zero_eta = theta[2] + theta[3] * row["z"]
    if model == "zero_inflated_poisson":
        return (
            -logadd(-softplus(-zero_eta), -softplus(zero_eta) - mu)
            if y == 0
            else softplus(zero_eta) + base
        )
    if model == "hurdle_poisson":
        return (
            softplus(-zero_eta)
            if y == 0
            else softplus(zero_eta) + base + math.log(-math.expm1(-mu))
        )
    raise ValueError("Unsupported independent density")


def row_moments(model, theta, row):
    if model == "normal":
        return theta[0], math.exp(2 * theta[1])
    if model == "linear_gaussian":
        return theta[0] + theta[1] * row["x"], math.exp(2 * theta[2])
    if model == "student_t_regression":
        nu = 2 + math.exp(theta[3])
        return theta[0] + theta[1] * row["x"], math.exp(2 * theta[2]) * nu / (nu - 2)
    eta = theta[0] + theta[1] * row["x"]
    if model in {"binomial_logistic", "beta_binomial"}:
        p = probability(eta)
        n = row["trials"]
        phi = math.exp(theta[2]) if model == "beta_binomial" else 0
        return n * p, n * p * probability(-eta) * ((n + phi) / (1 + phi) if phi else 1)
    mu = row["exposure"] * math.exp(eta)
    if model == "poisson_exposure":
        return mu, mu
    zero_eta = theta[2] + theta[3] * row["z"]
    nonzero = probability(-zero_eta)
    zero = probability(zero_eta)
    component_mean = mu
    component_variance = mu
    if model == "hurdle_poisson":
        norm = -math.expm1(-mu)
        component_mean = mu / norm
        component_variance = component_mean * (1 - mu * math.exp(-mu) / norm)
    return (
        nonzero * component_mean,
        nonzero * component_variance + zero * nonzero * component_mean**2,
    )


def named_oracle(case, method):
    rows = case["training"]
    n = len(rows)
    require(
        sum(row["x"] for row in rows) == 0 and sum(row["x"] ** 2 for row in rows) == n,
        "Analytic named-target oracle requires orthogonal [1,x] and known sigma1",
    )
    sy = math.fsum(row["y"] for row in rows)
    sxy = math.fsum(row["x"] * row["y"] for row in rows)
    penalty = method.get("regularization") or {"gaussian": {}, "l1": {}}
    prior = penalty["gaussian"].get("beta1", {"mean": 0, "precision": 0})
    lam = penalty["l1"].get("beta1", 0)
    precision = prior["precision"]
    numerator = sxy + precision * prior["mean"]
    slope = math.copysign(max(abs(numerator) - lam, 0), numerator) / (n + precision)
    theta = [sy / n, slope, 0]
    value = math.fsum(row_nll("linear_gaussian", theta, row) for row in rows)
    value += 0.5 * precision * (slope - prior["mean"]) ** 2 + lam * abs(slope)
    if precision:
        value += 0.5 * (math.log(2 * math.pi) - math.log(precision))
    smooth_gradient = [n * theta[0] - sy, (n + precision) * slope - numerator]
    kkt = max(
        abs(smooth_gradient[0]),
        max(abs(smooth_gradient[1]) - lam, 0)
        if slope == 0
        else abs(smooth_gradient[1] + math.copysign(lam, slope)),
    )
    return {
        "parameters": theta,
        "summed_target": value,
        "summed_kkt_inf": kkt,
        ("target"): (
            "Known-sigma Gaussian summed likelihood plus selected named penalty; intercept "
            "unpenalized"
        ),
    }


def prediction_metrics(case, model, theta, predictions):
    index = {row["row_id"]: row for row in predictions}
    require(
        len(index) == len(predictions) and set(index) == {r["row_id"] for r in case["future"]},
        "Future identity coverage differs",
    )
    groups = {}
    gaussian = model in {
        "normal",
        "linear_gaussian",
        "gaussian_correlated_random_slope",
    }
    for row in case["future"]:
        point = index[row["row_id"]]
        location = point["mean"]
        variance = point["variance"]
        require(
            math.isfinite(location) and math.isfinite(variance) and variance > 0,
            "Invalid predictive moments",
        )
        error = row["y"] - location
        nll = (
            gaussian_nll(row["y"], location, math.sqrt(variance))
            if gaussian
            else row_nll(model, theta, row)
        )
        item = {
            "squared_error": error**2,
            "nll": nll,
            "standardized_square": error**2 / variance,
            "unit": row.get("unit", "independent_rows"),
            "covered": abs(error) <= Z95 * math.sqrt(variance),
        }
        groups.setdefault(row.get("cohort", "future"), []).append(item)
    result = {}
    for cohort, records in groups.items():
        value = {
            "rows": len(records),
            "mse": mean([r["squared_error"] for r in records]),
            "mean_marginal_nll": mean([r["nll"] for r in records]),
            "mean_standardized_square": mean([r["standardized_square"] for r in records]),
            "score_distribution": model,
            ("uncertainty"): (
                "Plug-in observation/conditional latent moments; fixed parameter uncertainty "
                "omitted"
            ),
        }
        if gaussian:
            paths = {}
            for row in records:
                paths.setdefault(row["unit"], []).append(row["covered"])
            value.update(
                {
                    "gaussian_pointwise_coverage": mean([float(r["covered"]) for r in records]),
                    "unadjusted_gaussian_bands_path_coverage": mean(
                        [float(all(v)) for v in paths.values()]
                    ),
                }
            )
        result[cohort] = value
    return result


def cholesky(matrix):
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            residual = matrix[i][j] - math.fsum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                require(
                    residual > 0,
                    "Independent covariance factorization is not positive definite",
                )
                lower[i][j] = math.sqrt(residual)
            else:
                lower[i][j] = residual / lower[j][j]
    return lower


def solve_cholesky(lower, rhs):
    n = len(rhs)
    forward = [0.0] * n
    answer = [0.0] * n
    for i in range(n):
        forward[i] = (rhs[i] - math.fsum(lower[i][j] * forward[j] for j in range(i))) / lower[i][i]
    for i in range(n - 1, -1, -1):
        answer[i] = (
            forward[i] - math.fsum(lower[j][i] * answer[j] for j in range(i + 1, n))
        ) / lower[i][i]
    return answer


def panel_reference(theta, history, future):
    """Dense observation-covariance oracle, independent of native augmented QR."""
    beta0, beta1, log_sigma, log_tau0, log_tau1, atanh_rho = theta
    sigma2 = math.exp(2 * log_sigma)
    tau0 = math.exp(log_tau0)
    tau1 = math.exp(log_tau1)
    rho = math.tanh(atanh_rho)

    def kernel(x, z):
        return tau0 * tau0 + (x + z) * rho * tau0 * tau1 + x * z * tau1 * tau1

    grouped = {}
    for row in history:
        grouped.setdefault(row["unit"], []).append(row)
    factors = {}
    nll = 0.0
    for key, rows in grouped.items():
        covariance = [
            [kernel(a["x"], b["x"]) + (sigma2 if i == j else 0.0) for j, b in enumerate(rows)]
            for i, a in enumerate(rows)
        ]
        lower = cholesky(covariance)
        residual = [row["y"] - beta0 - beta1 * row["x"] for row in rows]
        answer = solve_cholesky(lower, residual)
        factors[key] = (rows, lower, answer)
        nll += 0.5 * (
            len(rows) * math.log(2 * math.pi)
            + 2 * math.fsum(math.log(lower[i][i]) for i in range(len(rows)))
            + math.fsum(a * b for a, b in zip(residual, answer, strict=True))
        )
    predictions = []
    for row in future:
        location = beta0 + beta1 * row["x"]
        variance = sigma2 + kernel(row["x"], row["x"])
        if row.get("cohort") == "known":
            rows, lower, answer = factors[row["unit"]]
            cross = [kernel(row["x"], observed["x"]) for observed in rows]
            location += math.fsum(a * b for a, b in zip(cross, answer, strict=True))
            inverse_cross = solve_cholesky(lower, cross)
            variance -= math.fsum(a * b for a, b in zip(cross, inverse_cross, strict=True))
        predictions.append({"row_id": row["row_id"], "mean": location, "variance": variance})
    return nll, predictions


def penalty_value(theta, names, regularization):
    if regularization is None:
        return 0.0
    index = dict(zip(names, theta, strict=True))
    return 0.5 * math.fsum(
        (
            v["precision"] * (index[name] - v["mean"]) ** 2
            + math.log(2 * math.pi)
            - math.log(v["precision"])
        )
        for name, v in regularization["gaussian"].items()
    ) + math.fsum(v * abs(index[name]) for name, v in regularization["l1"].items())
