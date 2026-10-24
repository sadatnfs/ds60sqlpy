"""torch-020: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Compare local reductions
    image = torch.tensor([[[[1.0, 3.0], [2.0, 4.0]]]])
    assert F.max_pool2d(image, 2).item() == 4 and F.avg_pool2d(image, 2).item() == 2.5

    # Exercise 2: Inspect a horizontal flip
    flipped = torch.flip(image, dims=(-1,))
    assert flipped[0, 0].tolist() == [[3.0, 1.0], [4.0, 2.0]]

    # Exercise 3: Check the round trip
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
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
