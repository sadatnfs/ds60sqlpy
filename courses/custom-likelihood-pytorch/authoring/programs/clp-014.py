"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def quadratic_nll(beta, design, y):
    return ((y - design @ beta).square() / 2).sum()


def profile_decay(time, rate_grid, sigma=0.1):
    y = 2 * torch.exp(-0.7 * time) + 0.4
    values = []
    for rate in rate_grid:
        design = torch.stack([torch.exp(-rate * time), torch.ones_like(time)], dim=1)
        amplitude, offset = torch.linalg.lstsq(design, y).solution
        if float(amplitude) <= 0:
            raise ValueError("This profile fixture expects an interior positive amplitude")
        values.append(((y - (amplitude * design[:, 0] + offset)).square() / (2 * sigma**2)).sum())
    return torch.stack(values)


def run_cases():
    x = tensor([1, 2, 3, 4])
    y = 3 * x + tensor([0.2, -0.2, -0.2, 0.2])
    duplicated = torch.stack([x, x], dim=1)
    hessian = torch.autograd.functional.hessian(
        lambda b: quadratic_nll(b, duplicated, y), tensor([1, 2])
    )
    eigen = torch.linalg.eigvalsh(hessian)
    assert abs(float(eigen[0])) < 1e-12
    loss_a = quadratic_nll(tensor([1, 2]), duplicated, y)
    loss_b = quadratic_nll(tensor([2, 1]), duplicated, y)
    assert loss_a == loss_b
    rates = torch.linspace(0.3, 1.1, 41, dtype=DTYPE)
    long = profile_decay(torch.linspace(0, 6, 25, dtype=DTYPE), rates)
    short = profile_decay(torch.linspace(0, 0.08, 25, dtype=DTYPE), rates)
    long_span = float(long.max() - long.min())
    short_span = float(short.max() - short.min())
    assert short_span < long_span / 1000
    assert abs(float(rates[torch.argmin(long)]) - 0.7) < 1e-12
    return {
        "rank_deficient_hessian_eigenvalues": eigen.tolist(),
        "same_sum_coefficients_same_nll": float(loss_a),
        "long_profile_contrast": long_span,
        "short_profile_contrast": short_span,
        "profile_rate_minimum": float(rates[torch.argmin(long)]),
        "finite_optimizer_output_does_not_establish_identification": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
