"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def scale_objective(log_sigma, residuals, *, false_parameter_jacobian=False):
    sigma = torch.exp(log_sigma)
    loss = (
        log_sigma + 0.5 * math.log(2 * math.pi) + residuals.square() / (2 * sigma.square())
    ).sum()
    return loss - log_sigma if false_parameter_jacobian else loss


def lognormal_log_density(x, mu, sigma):
    if bool((x <= 0).any()):
        raise ValueError("A lognormal observation must be positive")
    return torch.distributions.Normal(mu, sigma).log_prob(torch.log(x)) - torch.log(x)


def run_cases():
    residuals = tensor([-1, 1])
    s = tensor(0.0).requires_grad_()
    correct = torch.autograd.grad(scale_objective(s, residuals), s)[0]
    incorrect = torch.autograd.grad(
        scale_objective(s, residuals, false_parameter_jacobian=True), s
    )[0]
    assert float(correct) == 0 and float(incorrect) == -1
    x, mu, sigma = tensor([0.5, 2, 3]), tensor(0.3), tensor(0.7)
    manual = lognormal_log_density(x, mu, sigma)
    library = torch.distributions.LogNormal(mu, sigma).log_prob(x)
    assert torch.allclose(manual, library, atol=1e-12, rtol=0)
    grid = torch.exp(torch.linspace(-7, 7, 6001, dtype=DTYPE))
    integral = torch.trapezoid(torch.exp(lognormal_log_density(grid, mu, sigma)), grid)
    assert abs(float(integral) - 1) < 1e-5
    raw_rho = tensor(1.2).requires_grad_()
    rho = torch.tanh(raw_rho)
    dr = torch.autograd.grad(rho, raw_rho)[0]
    assert -1 < float(rho.detach()) < 1
    assert abs(float(dr) - (1 - float(rho.detach()) ** 2)) < 1e-12
    return {
        "correct_scale_gradient_at_mle": float(correct),
        "false_jacobian_gradient": float(incorrect),
        "lognormal_density_integral": float(integral),
        "rho": float(rho.detach()),
        "density_jacobian_needed_only_for_random_variable_change": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
