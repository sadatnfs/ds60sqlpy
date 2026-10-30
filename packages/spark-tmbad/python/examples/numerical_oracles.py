"""Independent small-model references for validation, never production execution.

No automatic differentiation, native model calls, NumPy or Spark are used here.
"""

from __future__ import annotations

import math

LOG_TWO_PI = math.log(2 * math.pi)


def gaussian_random_intercept(theta, observations):
    """Exact marginal value and analytic gradient from compound-symmetry eigenvalues."""
    beta, log_sigma, log_tau = theta
    n = len(observations)
    if not n:
        raise ValueError("An independent group must be nonempty")
    sigma2, tau2 = math.exp(2 * log_sigma), math.exp(2 * log_tau)
    average = math.fsum(observations) / n
    centered = math.fsum((value - average) ** 2 for value in observations)
    shift = average - beta
    mean_eigenvalue = sigma2 + n * tau2
    loss = 0.5 * (
        n * LOG_TWO_PI
        + (n - 1) * math.log(sigma2)
        + math.log(mean_eigenvalue)
        + centered / sigma2
        + n * shift * shift / mean_eigenvalue
    )
    gradient = [
        -n * shift / mean_eigenvalue,
        (n - 1)
        + sigma2 / mean_eigenvalue
        - centered / sigma2
        - n * shift * shift * sigma2 / mean_eigenvalue**2,
        n * tau2 / mean_eigenvalue - n * n * shift * shift * tau2 / mean_eigenvalue**2,
    ]
    posterior_variance = 1 / (1 / tau2 + n / sigma2)
    posterior_mean = posterior_variance * n * shift / sigma2
    return {
        "loss": loss,
        "gradient": gradient,
        "mode": posterior_mean,
        "latent_variance": posterior_variance,
        "curvature": 1 / posterior_variance,
    }


def gaussian_random_intercept_prediction(theta, observations=None):
    beta, log_sigma, log_tau = theta
    sigma2, tau2 = math.exp(2 * log_sigma), math.exp(2 * log_tau)
    if observations is None:
        mean, variance = beta, sigma2 + tau2
    else:
        posterior = gaussian_random_intercept(theta, observations)
        mean, variance = beta + posterior["mode"], sigma2 + posterior["latent_variance"]
    return [mean, variance, math.sqrt(variance)]


def poisson_joint(theta, rows, latent):
    """Normalized scalar Poisson/lognormal joint density, evaluated with ordinary math."""
    beta, log_tau = theta
    terms = [
        exposure * math.exp(beta + latent)
        - count * (beta + latent + math.log(exposure))
        + math.lgamma(count + 1)
        for exposure, count in rows
    ]
    return (
        math.fsum(terms)
        + log_tau
        + 0.5 * LOG_TWO_PI
        + 0.5 * latent * latent * math.exp(-2 * log_tau)
    )


def poisson_random_intercept(theta, rows):
    """One-dimensional Laplace reference with analytic mode/curvature/outer gradient.

    The strictly increasing scalar score provides a bracket. A safeguarded
    Newton solve avoids relying on tiny differences between joint loss values.
    The outer gradient includes the implicit mode derivative in the curvature.
    """
    beta, log_tau = theta
    if not rows or any(
        exposure <= 0 or count < 0 or count != int(count) for exposure, count in rows
    ):
        raise ValueError("Expected positive exposures and nonnegative integer counts")
    exposure_sum = math.fsum(row[0] for row in rows)
    count_sum = math.fsum(row[1] for row in rows)
    precision = math.exp(-2 * log_tau)

    def terms(latent):
        total_rate = exposure_sum * math.exp(beta + latent)
        return total_rate - count_sum + precision * latent, total_rate + precision, total_rate

    lower, upper = -1.0, 1.0
    while terms(lower)[0] > 0:
        lower *= 2
    while terms(upper)[0] < 0:
        upper *= 2
    latent = 0.0
    for _ in range(150):
        score, curvature, total_rate = terms(latent)
        if abs(score) <= 2e-13 * (1 + count_sum + abs(precision * latent)):
            break
        if score > 0:
            upper = latent
        else:
            lower = latent
        candidate = latent - score / curvature
        if not lower < candidate < upper:
            candidate = 0.5 * (lower + upper)
        if candidate == latent:
            break
        latent = candidate
    else:
        raise ArithmeticError("Independent bracketed mode solve failed")
    score, curvature, total_rate = terms(latent)
    if abs(score) > 1e-10 * (1 + count_sum):
        raise ArithmeticError("Independent mode does not satisfy its analytic score")
    latent_beta = -total_rate / curvature
    latent_scale = 2 * precision * latent / curvature
    gradient = [
        total_rate - count_sum + 0.5 * total_rate * (1 + latent_beta) / curvature,
        1
        - precision * latent * latent
        + 0.5 * (total_rate * latent_scale - 2 * precision) / curvature,
    ]
    return {
        "loss": poisson_joint(theta, rows, latent) + 0.5 * math.log(curvature) - 0.5 * LOG_TWO_PI,
        "gradient": gradient,
        "mode": latent,
        "score": score,
        "curvature": curvature,
        "latent_variance": 1 / curvature,
    }


def poisson_random_intercept_prediction(theta, exposure, history=None):
    """Prior exact moments, or moments under the local Gaussian Laplace posterior."""
    beta, log_tau = theta
    if history is None:
        latent_mean, latent_variance = 0.0, math.exp(2 * log_tau)
    else:
        reference = poisson_random_intercept(theta, history)
        latent_mean, latent_variance = reference["mode"], reference["latent_variance"]
    mean = exposure * math.exp(beta + latent_mean + 0.5 * latent_variance)
    variance = mean + mean * mean * math.expm1(latent_variance)
    return [mean, variance, math.sqrt(variance)]


def poisson_random_slope(theta, rows):
    """Analytic two-dimensional Laplace reference without automatic differentiation."""
    beta0, beta1, log_tau0, log_tau1 = theta
    precision = [math.exp(-2 * log_tau0), math.exp(-2 * log_tau1)]
    design = [[1.0, row[0]] for row in rows]

    def evaluate(latent):
        rates = [
            exposure * math.exp(beta0 + beta1 * x + latent[0] + latent[1] * x)
            for x, exposure, _ in rows
        ]
        joint = math.fsum(
            rate
            - count * (beta0 + beta1 * x + latent[0] + latent[1] * x + math.log(exposure))
            + math.lgamma(count + 1)
            for rate, (x, exposure, count) in zip(rates, rows, strict=True)
        )
        joint += (
            log_tau0
            + log_tau1
            + LOG_TWO_PI
            + 0.5 * math.fsum(q * u * u for q, u in zip(precision, latent, strict=True))
        )
        score = [
            math.fsum(
                (rate - row[2]) * a[index] for rate, row, a in zip(rates, rows, design, strict=True)
            )
            + precision[index] * latent[index]
            for index in range(2)
        ]
        hessian = [
            [
                math.fsum(rate * a[i] * a[j] for rate, a in zip(rates, design, strict=True))
                + (precision[i] if i == j else 0.0)
                for j in range(2)
            ]
            for i in range(2)
        ]
        return joint, score, hessian, rates

    latent = [0.0, 0.0]
    for _ in range(120):
        joint, score, hessian, rates = evaluate(latent)
        if max(map(abs, score)) <= 1e-11:
            break
        factor = _cholesky(hessian)
        step = _solve_cholesky(factor, [-value for value in score])
        slope = math.fsum(g * d for g, d in zip(score, step, strict=True))
        for trial in range(45):
            scale = 2.0**-trial
            candidate = [u + scale * d for u, d in zip(latent, step, strict=True)]
            proposed, proposed_score, _, _ = evaluate(candidate)
            ordinary = proposed <= joint + 1e-4 * scale * slope
            roundoff = proposed <= joint + 2e-14 * max(1.0, abs(joint)) and max(
                map(abs, proposed_score)
            ) < max(map(abs, score))
            if ordinary or roundoff:
                latent = candidate
                break
        else:
            raise ArithmeticError("Independent two-dimensional mode line search failed")
    else:
        raise ArithmeticError("Independent two-dimensional mode did not converge")
    joint, score, hessian, rates = evaluate(latent)
    factor = _cholesky(hessian)
    inverse_columns = [_solve_cholesky(factor, [float(i == j) for i in range(2)]) for j in range(2)]
    gradient = []
    for parameter in range(4):
        if parameter < 2:
            mixed = [
                math.fsum(rate * a[i] * a[parameter] for rate, a in zip(rates, design, strict=True))
                for i in range(2)
            ]
            mode_derivative = _solve_cholesky(factor, [-value for value in mixed])
            direct = math.fsum(
                (rate - row[2]) * a[parameter]
                for rate, row, a in zip(rates, rows, design, strict=True)
            )
        else:
            index = parameter - 2
            mode_derivative = _solve_cholesky(
                factor,
                [2 * precision[index] * latent[index] if i == index else 0.0 for i in range(2)],
            )
            direct = 1 - precision[index] * latent[index] ** 2
        curvature_derivative = [[0.0] * 2 for _ in range(2)]
        for i in range(2):
            for j in range(2):
                curvature_derivative[i][j] = math.fsum(
                    rate
                    * a[i]
                    * a[j]
                    * (
                        (a[parameter] if parameter < 2 else 0.0)
                        + math.fsum(
                            z * derivative for z, derivative in zip(a, mode_derivative, strict=True)
                        )
                    )
                    for rate, a in zip(rates, design, strict=True)
                )
                if parameter >= 2 and i == j == parameter - 2:
                    curvature_derivative[i][j] -= 2 * precision[i]
        trace = math.fsum(
            inverse_columns[i][j] * curvature_derivative[i][j] for i in range(2) for j in range(2)
        )
        gradient.append(direct + 0.5 * trace)
    return {
        "loss": joint + math.fsum(math.log(factor[i][i]) for i in range(2)) - LOG_TWO_PI,
        "gradient": gradient,
        "mode": latent,
        "score": score,
        "latent_covariance": [[inverse_columns[j][i] for j in range(2)] for i in range(2)],
    }


def poisson_random_slope_prediction(theta, x, exposure, history=None):
    beta0, beta1, log_tau0, log_tau1 = theta
    if history is None:
        latent_mean = 0.0
        latent_variance = math.exp(2 * log_tau0) + x * x * math.exp(2 * log_tau1)
    else:
        posterior = poisson_random_slope(theta, history)
        latent_mean = posterior["mode"][0] + x * posterior["mode"][1]
        covariance = posterior["latent_covariance"]
        latent_variance = covariance[0][0] + 2 * x * covariance[0][1] + x * x * covariance[1][1]
    mean = exposure * math.exp(beta0 + beta1 * x + latent_mean + 0.5 * latent_variance)
    variance = mean + mean * mean * math.expm1(latent_variance)
    return [mean, variance, math.sqrt(variance)]


def ar1_forecast(theta, horizons, last_observation=None):
    """Direct finite sums of independent innovation variances at known parameters."""
    mu, unconstrained_phi, log_sigma = theta
    phi, sigma2 = math.tanh(unconstrained_phi), math.exp(2 * log_sigma)
    result = []
    for horizon in horizons:
        if type(horizon) is not int or horizon < 1:
            raise ValueError("Forecast horizons must be positive integers")
        if last_observation is None:
            mean, variance = mu, sigma2 / (1 - phi * phi)
        else:
            mean = mu + phi**horizon * (last_observation - mu)
            variance = sigma2 * math.fsum(phi ** (2 * j) for j in range(horizon))
        result.append([mean, variance, math.sqrt(variance)])
    return result


def _cholesky(matrix):
    size = len(matrix)
    factor = [[0.0] * size for _ in range(size)]
    for row in range(size):
        for column in range(row + 1):
            remainder = matrix[row][column] - math.fsum(
                factor[row][index] * factor[column][index] for index in range(column)
            )
            if row == column:
                if remainder <= 0:
                    raise ArithmeticError("Reference covariance is not positive definite")
                factor[row][column] = math.sqrt(remainder)
            else:
                factor[row][column] = remainder / factor[column][column]
    return factor


def _solve_cholesky(factor, vector):
    size = len(vector)
    forward, solution = [0.0] * size, [0.0] * size
    for row in range(size):
        forward[row] = (
            vector[row] - math.fsum(factor[row][column] * forward[column] for column in range(row))
        ) / factor[row][row]
    for row in range(size - 1, -1, -1):
        solution[row] = (
            forward[row]
            - math.fsum(factor[column][row] * solution[column] for column in range(row + 1, size))
        ) / factor[row][row]
    return solution


def _combined_covariance(theta, left_times, right_times):
    _, unconstrained_phi, log_sigma, log_tau = theta
    phi = math.tanh(unconstrained_phi)
    stationary_variance = math.exp(2 * log_sigma) / (1 - phi * phi)
    tau2 = math.exp(2 * log_tau)
    return [
        [tau2 + stationary_variance * phi ** abs(left - right) for right in right_times]
        for left in left_times
    ]


def gaussian_ar1_random_intercept(theta, rows):
    """Exact F/G from dense covariance, independent of an AR precision reduction."""
    beta, unconstrained_phi, log_sigma, log_tau = theta
    times, observations = [row[0] for row in rows], [row[1] for row in rows]
    size = len(rows)
    if not size:
        raise ValueError("A complete history must be nonempty")
    phi, sigma2, tau2 = math.tanh(unconstrained_phi), math.exp(2 * log_sigma), math.exp(2 * log_tau)
    covariance = _combined_covariance(theta, times, times)
    factor = _cholesky(covariance)
    residual = [value - beta for value in observations]
    score = _solve_cholesky(factor, residual)
    loss = 0.5 * (
        size * LOG_TWO_PI
        + 2 * math.fsum(math.log(factor[i][i]) for i in range(size))
        + math.fsum(left * right for left, right in zip(residual, score, strict=True))
    )
    inverse_columns = [
        _solve_cholesky(factor, [float(i == j) for i in range(size)]) for j in range(size)
    ]
    covariance_derivatives = [[[0.0] * size for _ in range(size)] for _ in range(3)]
    for row in range(size):
        for column in range(size):
            distance = abs(times[row] - times[column])
            ar_covariance = sigma2 * phi**distance / (1 - phi * phi)
            covariance_derivatives[0][row][column] = 2 * phi * ar_covariance + (
                sigma2 * distance * phi ** (distance - 1) if distance else 0.0
            )
            covariance_derivatives[1][row][column] = 2 * ar_covariance
            covariance_derivatives[2][row][column] = 2 * tau2
    gradient = [-math.fsum(score)]
    for derivative in covariance_derivatives:
        trace = math.fsum(
            inverse_columns[row][column] * derivative[row][column]
            for row in range(size)
            for column in range(size)
        )
        quadratic = math.fsum(
            score[row] * derivative[row][column] * score[column]
            for row in range(size)
            for column in range(size)
        )
        gradient.append(0.5 * (trace - quadratic))
    return {"loss": loss, "gradient": gradient}


def gaussian_ar1_random_intercept_prediction(theta, future_times, history=None):
    """Dense joint-Gaussian conditioning, reporting per-row observation moments."""
    beta = theta[0]
    future_covariance = _combined_covariance(theta, future_times, future_times)
    if history is None:
        return [
            [beta, future_covariance[index][index], math.sqrt(future_covariance[index][index])]
            for index in range(len(future_times))
        ]
    history_times = [row[0] for row in history]
    residual = [row[1] - beta for row in history]
    history_covariance = _combined_covariance(theta, history_times, history_times)
    cross = _combined_covariance(theta, future_times, history_times)
    factor = _cholesky(history_covariance)
    score = _solve_cholesky(factor, residual)
    result = []
    for index, weights in enumerate(cross):
        mean = beta + math.fsum(left * right for left, right in zip(weights, score, strict=True))
        solution = _solve_cholesky(factor, weights)
        variance = future_covariance[index][index] - math.fsum(
            left * right for left, right in zip(weights, solution, strict=True)
        )
        result.append([mean, variance, math.sqrt(variance)])
    return result


def finite_difference_gradient(function, theta, step):
    result = []
    for index, value in enumerate(theta):
        lower, upper = list(theta), list(theta)
        lower[index], upper[index] = value - step, value + step
        result.append((function(upper) - function(lower)) / (2 * step))
    return result


def finite_difference_hessian(gradient_function, theta, step):
    """Return row-major Hessian entries by differencing an independent gradient."""
    dimension = len(theta)
    result = [0.0] * (dimension * dimension)
    for column, value in enumerate(theta):
        lower, upper = list(theta), list(theta)
        lower[column], upper[column] = value - step, value + step
        low, high = gradient_function(lower), gradient_function(upper)
        for row in range(dimension):
            result[row * dimension + column] = (high[row] - low[row]) / (2 * step)
    return result
