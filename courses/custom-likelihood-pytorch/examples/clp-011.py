"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def mixture_log_prob(y, logits, means, scales):
    if (
        y.ndim != 1
        or logits.ndim != 1
        or means.shape != logits.shape
        or scales.shape != logits.shape
        or not len(logits)
    ):
        raise ValueError("Use observations and matching component vectors")
    if not bool(
        torch.isfinite(y).all()
        & torch.isfinite(logits).all()
        & torch.isfinite(means).all()
        & torch.isfinite(scales).all()
    ) or bool((scales <= 0).any()):
        raise ValueError("All mixture inputs must be finite, with positive scales")
    component = torch.distributions.Normal(means, scales).log_prob(y[:, None])
    return torch.logsumexp(torch.log_softmax(logits, dim=0) + component, dim=1)


def run_cases():
    logits, means, scales = tensor([0.3, -0.2]), tensor([-2, 2]), tensor([1, 1])
    y = tensor([-1, 0, 2.5, 100])
    stable = mixture_log_prob(y, logits, means, scales)
    library = torch.distributions.MixtureSameFamily(
        torch.distributions.Categorical(logits=logits), torch.distributions.Normal(means, scales)
    ).log_prob(y)
    swapped = mixture_log_prob(y, logits.flip(0), means.flip(0), scales.flip(0))
    assert torch.allclose(stable, library, atol=1e-12, rtol=0) and torch.allclose(
        stable, swapped, atol=1e-12, rtol=0
    )
    direct = (
        torch.softmax(logits, dim=0)
        * torch.exp(torch.distributions.Normal(means, scales).log_prob(y[-1]))
    ).sum()
    assert float(direct) == 0 and bool(torch.isfinite(stable).all())
    collapse = [
        float(mixture_log_prob(tensor([0]), tensor([0, 0]), tensor([0, 3]), tensor([s, 1]))[0])
        for s in (1, 0.1, 0.01)
    ]
    assert collapse[0] < collapse[1] < collapse[2]
    return {
        "stable_log_probabilities": stable.tolist(),
        "direct_probability_underflowed": float(direct) == 0,
        "label_swap_invariant": True,
        "single_point_collapse_log_likelihood": collapse,
        "scale_collapse_is_not_model_success": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
