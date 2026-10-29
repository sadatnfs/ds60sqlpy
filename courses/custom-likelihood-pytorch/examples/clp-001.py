"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def bernoulli_nll(probability, observations):
    p, y = tensor(probability), tensor(observations)
    if p.ndim != 0 or not bool(torch.isfinite(p)) or not 0 < float(p.detach()) < 1:
        raise ValueError("Use one interior Bernoulli probability")
    if y.ndim != 1 or not len(y) or not bool(torch.all((y == 0) | (y == 1))):
        raise ValueError("Use a nonempty binary observation vector")
    return -(y * torch.log(p) + (1 - y) * torch.log1p(-p)).sum()


def shared_subject_probability(observations, latent_probabilities):
    y, probabilities = tensor(observations), tensor(latent_probabilities)
    if probabilities.ndim != 1 or not len(probabilities):
        raise ValueError("Use a nonempty finite latent mixture")
    conditional = torch.stack([torch.exp(-bernoulli_nll(p, y)) for p in probabilities])
    return conditional.mean()


def run_cases():
    y = tensor([1, 1, 0])
    p = tensor(0.4).requires_grad_()
    loss = bernoulli_nll(p, y)
    expected = -math.log(0.4 * 0.4 * 0.6)
    distribution = -torch.distributions.Bernoulli(probs=p).log_prob(y).sum()
    gradient = torch.autograd.grad(loss, p)[0]
    assert torch.allclose(loss, distribution)
    assert abs(float(loss.detach()) - expected) < 1e-12
    assert abs(float(gradient) - (-2 / 0.4 + 1 / 0.6)) < 1e-12
    shared = shared_subject_probability([1, 1], [0.2, 0.8])
    independent = tensor(0.5**2)
    assert abs(float(shared) - 0.34) < 1e-12
    assert float(shared) > float(independent)
    return {
        "independent_nll": float(loss.detach()),
        "probability_gradient": float(gradient),
        "same_subject_two_successes": float(shared),
        "independent_marginal_two_successes": float(independent),
        "observation_units": "three independent trials versus one repeated subject",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
