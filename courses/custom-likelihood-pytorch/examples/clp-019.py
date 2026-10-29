"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
from collections import Counter

import torch
from torch.utils.data import DistributedSampler

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def gradient_of_mean(y, mu=3.0):
    parameter = tensor(mu).requires_grad_()
    loss = (y - parameter).square().mean() / 2
    return torch.autograd.grad(loss, parameter)[0]


def run_cases():
    y = tensor([0, 2, 4, 8, 10, 12])
    shards = [y[:2], y[2:]]
    world = len(shards)
    total = len(y)
    global_gradient = gradient_of_mean(y)
    local_means = [gradient_of_mean(part) for part in shards]
    naive = torch.stack(local_means).mean()
    corrected = torch.stack(
        [g * world * len(part) / total for g, part in zip(local_means, shards, strict=True)]
    ).mean()
    torch.testing.assert_close(global_gradient, tensor(-3.0))
    torch.testing.assert_close(naive, tensor(-1.75))
    assert torch.allclose(corrected, global_gradient, atol=1e-12, rtol=0)
    dataset = range(5)
    padded = [
        list(DistributedSampler(dataset, num_replicas=2, rank=rank, shuffle=False, drop_last=False))
        for rank in range(2)
    ]
    dropped = [
        list(DistributedSampler(dataset, num_replicas=2, rank=rank, shuffle=False, drop_last=True))
        for rank in range(2)
    ]
    padded_counts = Counter(index for part in padded for index in part)
    dropped_ids = {index for part in dropped for index in part}
    assert padded_counts[0] == 2 and dropped_ids == {0, 1, 2, 3}
    return {
        "global_mean_gradient": float(global_gradient),
        "naive_average_of_rank_mean_gradients": float(naive),
        "corrected_ddp_average": float(corrected),
        "rank_loss_multipliers": [world * len(part) / total for part in shards],
        "padded_sampler_indices": padded,
        "drop_last_sampler_indices": dropped,
        "execution": (
            "serial gradient arithmetic and actual sampler inspection; no distributed process group"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
