"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def poisson_nll(log_rate, counts, exposure):
    if counts.ndim != 1 or exposure.shape != counts.shape or not len(counts):
        raise ValueError("Use matching count and exposure vectors")
    if (
        not bool(torch.isfinite(counts).all() & torch.isfinite(exposure).all())
        or bool((counts < 0).any())
        or bool((counts != counts.floor()).any())
        or bool((exposure <= 0).any())
    ):
        raise ValueError("Use finite nonnegative integer counts and strictly positive exposure")
    log_mean = log_rate + torch.log(exposure)
    return (torch.exp(log_mean) - counts * log_mean + torch.lgamma(counts + 1)).sum()


def fit_rate(counts, exposure):
    poisson_nll(tensor(0.0), counts, exposure)
    if float(counts.sum()) == 0:
        raise ValueError("All-zero counts have a boundary zero-rate MLE, not a finite log rate")
    return counts.sum() / exposure.sum()


def run_cases():
    counts, exposure = tensor([0, 2, 1, 4]), tensor([1, 2, 1, 4])
    rate = fit_rate(counts, exposure)
    log_rate = rate.log().detach().requires_grad_()
    manual = poisson_nll(log_rate, counts, exposure)
    library = -torch.distributions.Poisson(exposure * log_rate.exp()).log_prob(counts).sum()
    derivative = torch.autograd.grad(manual, log_rate)[0]
    assert float(rate) == 0.875 and abs(float(derivative)) < 1e-12
    assert torch.allclose(manual, library, atol=1e-12, rtol=0)
    predicted = rate * tensor([1.0, 2.0, 5.0])
    assert predicted[1] == 2 * predicted[0]
    return {
        "rate_per_exposure_unit": float(rate),
        "naive_count_mean": float(counts.mean()),
        "nll": float(manual.detach()),
        "score_at_mle": float(derivative),
        "expected_counts_for_exposure_1_2_5": predicted.tolist(),
        "offset": "log exposure, with fixed unit coefficient",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
