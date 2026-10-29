"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def gaussian_nll(theta, design, y):
    coefficients, log_sigma = theta[:-1], theta[-1]
    if theta.ndim != 1 or design.shape != (len(y), len(coefficients)):
        raise ValueError("Parameter and design dimensions do not match")
    residual = y - design @ coefficients
    return (
        log_sigma + 0.5 * math.log(2 * math.pi) + residual.square() * torch.exp(-2 * log_sigma) / 2
    ).sum()


def fit_gaussian(design, y):
    if torch.linalg.matrix_rank(design) != design.shape[1]:
        raise ValueError("A unique coefficient MLE requires full column rank")
    closed = torch.linalg.lstsq(design, y).solution
    sigma = torch.sqrt(torch.mean((y - design @ closed).square()))
    roundoff = 20 * torch.finfo(DTYPE).eps * max(1.0, float(y.abs().max()))
    if float(sigma) <= roundoff:
        raise ValueError("Perfect interpolation has no interior positive-scale MLE")
    theta = torch.cat([torch.zeros(design.shape[1], dtype=DTYPE), tensor([0.0])]).requires_grad_()
    optimizer = torch.optim.LBFGS(
        [theta],
        max_iter=100,
        tolerance_grad=1e-10,
        tolerance_change=1e-13,
        line_search_fn="strong_wolfe",
    )

    def closure():
        optimizer.zero_grad()
        value = gaussian_nll(theta, design, y)
        value.backward()
        return value

    optimizer.step(closure)
    gradient = torch.autograd.grad(gaussian_nll(theta, design, y), theta)[0]
    return theta.detach(), closed, sigma, float(gradient.abs().max())


def run_cases():
    x, y = tensor([0, 1, 2, 3, 4]), tensor([1.1, 2.8, 5.2, 6.9, 9.0])
    design = torch.stack([torch.ones_like(x), x], dim=1)
    theta, closed, sigma, grad = fit_gaussian(design, y)
    assert torch.allclose(theta[:-1], closed, atol=2e-6, rtol=0)
    assert abs(float(theta[-1].exp()) - float(sigma)) < 2e-6
    centered = torch.stack([torch.ones_like(x), x - x.mean()], dim=1)
    ct, _, _, _ = fit_gaussian(centered, y)
    assert torch.allclose(design @ theta[:-1], centered @ ct[:-1], atol=3e-6, rtol=0)
    assert grad < 2e-4
    return {
        "coefficients": theta[:-1].tolist(),
        "sigma_mle": float(sigma),
        "sigma_unbiased_variance_root": float(sigma * math.sqrt(len(y) / (len(y) - 2))),
        "centered_intercept": float(ct[0]),
        "gradient_max_abs": grad,
        "nll": float(gaussian_nll(theta, design, y)),
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
