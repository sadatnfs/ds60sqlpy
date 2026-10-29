"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def normal_mean_nll(mu, y, sigma):
    mu, y, sigma = tensor(mu), tensor(y), tensor(sigma)
    if sigma.ndim != 0 or float(sigma) <= 0:
        raise ValueError("Use a positive known scale")
    return (
        torch.log(sigma) + 0.5 * math.log(2 * math.pi) + (y - mu).square() / (2 * sigma.square())
    ).sum()


def decay_nll(theta, time, y):
    mean = theta[0] * torch.exp(-theta[1] * time)
    return ((y - mean).square() / 2).sum()


def central_difference(function, theta, step):
    if not 0 < step < 1:
        raise ValueError("Use a positive small finite-difference step")
    basis = torch.eye(theta.numel(), dtype=DTYPE)
    return torch.stack(
        [
            (function(theta + step * row) - function(theta - step * row)) / (2 * step)
            for row in basis
        ]
    )


def run_cases():
    mu = tensor(0.3).requires_grad_()
    y = tensor([-1, 0.5, 2])
    loss = normal_mean_nll(mu, y, 1.5)
    derivative = torch.autograd.grad(loss, mu)[0]
    analytic = (mu.detach() - y).sum() / 1.5**2
    assert torch.allclose(derivative, analytic, atol=1e-12, rtol=0)
    theta = tensor([2.0, 0.7]).requires_grad_()
    time, observed = tensor([0, 1, 2]), tensor([1.9, 1.1, 0.4])

    def objective(value):
        return decay_nll(value, time, observed)

    ad = torch.autograd.grad(objective(theta), theta)[0]
    exponent = torch.exp(-theta.detach()[1] * time)
    residual = theta.detach()[0] * exponent - observed
    expected = torch.stack(
        [(residual * exponent).sum(), (residual * -theta.detach()[0] * time * exponent).sum()]
    )
    errors = {
        str(h): float((central_difference(objective, theta.detach(), h) - ad).abs().max())
        for h in (1e-3, 1e-5, 1e-7)
    }
    assert torch.allclose(ad, expected, atol=1e-12, rtol=0)
    assert min(errors.values()) < 1e-8
    return {
        "normal_mean_gradient": float(derivative),
        "nonlinear_gradient": ad.tolist(),
        "finite_difference_max_errors": errors,
        "precision": "float64",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
