"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def censored_exponential_nll(log_rate, times, event, entry=None):
    entry = torch.zeros_like(times) if entry is None else entry
    if (
        times.ndim != 1
        or not len(times)
        or event.shape != times.shape
        or entry.shape != times.shape
    ):
        raise ValueError("Use matching duration, event and entry vectors")
    if (
        not bool(torch.isfinite(times).all() & torch.isfinite(entry).all())
        or bool((entry < 0).any())
        or bool((times <= entry).any())
        or not bool(torch.all((event == 0) | (event == 1)))
    ):
        raise ValueError("Require finite 0 <= entry < exit and binary event status")
    return (log_rate.exp() * (times - entry) - event * log_rate).sum()


def mle(times, event, entry=None):
    censored_exponential_nll(tensor(0.0), times, event, entry)
    if float(event.sum()) == 0:
        raise ValueError("No events gives a boundary zero-rate estimate")
    entry = torch.zeros_like(times) if entry is None else entry
    return event.sum() / (times - entry).sum()


def run_cases():
    times, event = tensor([1, 2, 4, 5, 8]), tensor([1, 1, 0, 1, 0])
    rate = mle(times, event)
    changed = event.clone()
    changed[1] = 0
    changed_rate = mle(times, changed)
    delayed = mle(times, event, tensor([0, 0.5, 1, 0, 2]))
    lr = rate.log().detach().requires_grad_()
    score = torch.autograd.grad(censored_exponential_nll(lr, times, event), lr)[0]
    assert float(rate) == 0.15 and float(changed_rate) == 0.1 and abs(float(score)) < 1e-12
    assert abs(float(delayed) - 3 / 16.5) < 1e-12
    survival = float(torch.exp(-rate * tensor(4.0)))
    return {
        "right_censored_rate": float(rate),
        "one_fewer_event_rate": float(changed_rate),
        "incorrect_all_events_rate": len(times) / float(times.sum()),
        "delayed_entry_rate": float(delayed),
        "survival_at_4": survival,
        "score_at_mle": float(score),
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
