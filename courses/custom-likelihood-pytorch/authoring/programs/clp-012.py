"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def ar1_covariance(length, sigma, rho):
    sigma, rho = tensor(sigma), tensor(rho)
    if (
        length < 1
        or sigma.ndim != 0
        or rho.ndim != 0
        or not bool(torch.isfinite(sigma) & torch.isfinite(rho))
        or float(sigma) <= 0
        or abs(float(rho)) >= 1
    ):
        raise ValueError("Require positive scale and an interior stationary correlation")
    index = torch.arange(length)
    distance = (index[:, None] - index[None, :]).abs()
    return sigma.square() * rho.pow(distance)


def panel_nll(residuals, sigma, rho):
    if residuals.ndim != 2 or residuals.numel() == 0 or not bool(torch.isfinite(residuals).all()):
        raise ValueError("Use a finite nonempty matrix of independent complete panels")
    groups, length = residuals.shape
    covariance = ar1_covariance(length, sigma, rho)
    factor = torch.linalg.cholesky(covariance)
    whitened = torch.linalg.solve_triangular(factor, residuals.T, upper=False)
    return (
        groups * (length * math.log(2 * math.pi) / 2 + torch.log(torch.diag(factor)).sum())
        + whitened.square().sum() / 2
    )


def run_cases():
    residuals = tensor([[0.4, 0.2, -0.1], [-0.3, 0.1, 0.2]])
    sigma, rho = 0.5, 0.6
    correct = panel_nll(residuals, sigma, rho)
    distribution = torch.distributions.MultivariateNormal(
        torch.zeros(3, dtype=DTYPE), covariance_matrix=ar1_covariance(3, sigma, rho)
    )
    independent_oracle = -distribution.log_prob(residuals).sum()
    diagonal = panel_nll(residuals, sigma, 0.0)
    iid = -torch.distributions.Normal(tensor(0), tensor(sigma)).log_prob(residuals).sum()
    wrong = panel_nll(residuals.reshape(1, -1), sigma, rho)
    assert torch.allclose(correct, independent_oracle, atol=1e-12, rtol=0)
    assert torch.allclose(diagonal, iid, atol=1e-12, rtol=0)
    assert abs(float(correct - wrong)) > 1e-4
    return {
        "two_independent_panel_nll": float(correct),
        "wrong_cross_boundary_nll": float(wrong),
        "rho_zero_nll": float(diagonal),
        "panel_covariance": ar1_covariance(3, sigma, rho).tolist(),
        "independent_units": 2,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
