"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def weighted_loss(mu, observations, weights):
    y, w, mu = tensor(observations), tensor(weights), tensor(mu)
    if y.ndim != 1 or not len(y) or y.shape != w.shape:
        raise ValueError("One weight is required for each observation")
    if (
        not bool(torch.isfinite(y).all() & torch.isfinite(w).all())
        or bool((w < 0).any())
        or float(w.sum()) <= 0
    ):
        raise ValueError("Use finite observations and nonnegative positive-mass weights")
    numerator = (w * (y - mu).square() / 2).sum()
    return numerator, w.sum()


def run_cases():
    y, weights = tensor([0, 2, 4, 8, 10]), tensor([1, 1, 2, 1, 3])
    mu = tensor(3.0).requires_grad_()
    total, mass = weighted_loss(mu, y, weights)
    mean = total / mass
    a, wa = weighted_loss(mu, y[:2], weights[:2])
    b, wb = weighted_loss(mu, y[2:], weights[2:])
    wrong = (a / wa + b / wb) / 2
    right = (a + b) / (wa + wb)
    gradient = torch.autograd.grad(mean, mu)[0]
    assert float(total.detach()) == 92 and float(mass) == 8
    assert float(mean.detach()) == 11.5 and float(wrong.detach()) == 8.5
    assert torch.allclose(mean, right) and float(gradient) == -3
    scaled, scaled_mass = weighted_loss(mu, y, 7 * weights)
    assert torch.allclose(scaled / scaled_mass, mean)
    assert torch.allclose(scaled, 7 * total)
    return {
        "weighted_sum": float(total.detach()),
        "weight_mass": float(mass),
        "weighted_mean": float(mean.detach()),
        "wrong_equal_partition_mean": float(wrong.detach()),
        "global_mean_gradient": float(gradient),
        "frequency_weight_sum_changes_with_replication": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
