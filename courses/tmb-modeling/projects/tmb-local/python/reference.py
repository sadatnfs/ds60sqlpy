"""Independent standard-library algebra, not evidence of TMB execution."""

import math


def gaussian_value_gradient(y, mu, log_sigma):
    if len(y) < 2 or not all(math.isfinite(v) for v in [*y, mu, log_sigma]):
        raise ValueError("Finite observations and parameters required")
    variance = math.exp(2 * log_sigma)
    residual = [v - mu for v in y]
    square = sum(r * r for r in residual)
    value = len(y) * (log_sigma + 0.5 * math.log(2 * math.pi)) + square / (2 * variance)
    return value, [-sum(residual) / variance, len(y) - square / variance]


def weibull_nll(time, entry, event, scale, shape):
    if not (len(time) == len(entry) == len(event)) or not time:
        raise ValueError("Lengths must agree")
    if not all(math.isfinite(v) for v in [scale, shape]) or min(scale, shape) <= 0:
        raise ValueError("Positive finite scale and shape required")
    result = 0.0
    for t, a, d in zip(time, entry, event, strict=True):
        if not all(math.isfinite(v) for v in [t, a, d]) or not 0 <= a < t or d not in (0, 1):
            raise ValueError("Invalid censoring record")
        result += (
            (t / scale) ** shape
            - (a / scale) ** shape
            - d * (math.log(shape / scale) + (shape - 1) * math.log(t / scale))
        )
    return result


def ar1_precision(n, phi, tau):
    if (
        isinstance(n, bool)
        or not isinstance(n, int)
        or n < 1
        or not math.isfinite(phi)
        or not -1 < phi < 1
        or not math.isfinite(tau)
        or tau <= 0
    ):
        raise ValueError("Stationary AR1 domain required")
    if n == 1:
        return [[1 / tau**2]]
    scale = 1 / (tau**2 * (1 - phi**2))
    return [
        [
            scale
            * (
                (1 if i in (0, n - 1) else 1 + phi**2)
                if i == j
                else (-phi if abs(i - j) == 1 else 0)
            )
            for j in range(n)
        ]
        for i in range(n)
    ]


def gaussian_laplace(joint_at_mode, hessian_determinant, latent_dimension):
    if hessian_determinant <= 0 or not math.isfinite(hessian_determinant):
        raise ValueError("Positive definite Hessian required, determinant alone is insufficient")
    return (
        joint_at_mode
        + 0.5 * math.log(hessian_determinant)
        - 0.5 * latent_dimension * math.log(2 * math.pi)
    )
