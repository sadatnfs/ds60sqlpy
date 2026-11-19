"""torch-020: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Compare local reductions
    image = torch.tensor([[[[1.0, 3.0], [2.0, 4.0]]]])
    assert F.max_pool2d(image, 2).item() == 4 and F.avg_pool2d(image, 2).item() == 2.5

    # Worked example B: Inspect a horizontal flip
    flipped = torch.flip(image, dims=(-1,))
    assert flipped[0, 0].tolist() == [[3.0, 1.0], [4.0, 2.0]]

    # Worked example C: Check the round trip
    assert torch.equal(torch.flip(flipped, dims=(-1,)), image)

    # Exercise 4: Expose discarded information
    changed = image.clone()
    changed[0, 0, 0, 0] = 0
    assert F.max_pool2d(changed, 2).item() == 4 and F.avg_pool2d(changed, 2).item() == 2.25

    # Exercise 5: Keep evaluation transforms deterministic
    def transform(value, training):
        return torch.flip(value, (-1,)) if training else value.clone()

    evaluated = transform(image, False)
    assert torch.equal(evaluated, image)
    evaluated[0, 0, 0, 0] = 99
    assert image[0, 0, 0, 0].item() == 1

    # Exercise 6: Transform directional labels consistently
    labels = {"left": "right", "right": "left"}
    assert labels["left"] == "right" and labels[labels["left"]] == "left"

    # Exercise 1: Pool a new patch
    patch = torch.tensor([[[[5.0, -1.0], [2.0, 6.0]]]])
    assert F.max_pool2d(patch, 2).item() == 6 and F.avg_pool2d(patch, 2).item() == 3

    # Exercise 2: Flip the height axis instead
    vertical = torch.flip(patch, dims=(-2,))
    assert vertical[0, 0].tolist() == [[2.0, 6.0], [5.0, -1.0]]

    # Exercise 3: Pool a 4-by-4 map
    grid = torch.arange(16.0).reshape(1, 1, 4, 4)
    assert F.max_pool2d(grid, 2).tolist() == [[[[5.0, 7.0], [13.0, 15.0]]]] and F.avg_pool2d(
        grid, 2
    ).tolist() == [[[[2.5, 4.5], [10.5, 12.5]]]]
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
