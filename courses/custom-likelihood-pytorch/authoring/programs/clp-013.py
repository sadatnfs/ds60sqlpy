"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def data_nll(mu, y):
    return ((y - mu).square() / 2 + 0.5 * math.log(2 * math.pi)).sum()


def penalized(mu, y, precision):
    if precision < 0:
        raise ValueError("Penalty precision must be nonnegative")
    return data_nll(mu, y) + precision * mu.square() / 2


def run_cases():
    y = tensor([1, 2, 4])
    precision = 2.0
    mu = tensor(0.8).requires_grad_()
    full = penalized(mu, y, precision)
    once = data_nll(mu, y[:1]) + data_nll(mu, y[1:]) + precision * mu.square() / 2
    duplicated = penalized(mu, y[:1], precision) + penalized(mu, y[1:], precision)
    prior = torch.distributions.Normal(tensor(0), tensor(1 / math.sqrt(precision)))
    map_objective = data_nll(mu, y) - prior.log_prob(mu)
    grad_full = torch.autograd.grad(full, mu)[0]
    grad_map = torch.autograd.grad(map_objective, mu)[0]
    assert torch.allclose(full, once) and torch.allclose(grad_full, grad_map, atol=1e-12, rtol=0)
    assert torch.allclose(duplicated - full, precision * mu.square() / 2)
    mle = float(y.mean())
    penalized_fit = float(y.sum() / (len(y) + precision))
    duplicate_fit = float(y.sum() / (len(y) + 2 * precision))
    assert duplicate_fit < penalized_fit < mle
    return {
        "mle": mle,
        "penalized_mean": penalized_fit,
        "duplicated_penalty_mean": duplicate_fit,
        "penalty_count": 1,
        "map_minus_penalized_constant": float((map_objective - full).detach()),
        "gradient_equivalence": float(grad_full),
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
