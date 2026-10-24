"""torch-019: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Compute the fixed spatial filter
    image = torch.arange(1, 10, dtype=torch.float64).reshape(1, 1, 3, 3)
    kernel = torch.tensor([[[[1.0, 0.0], [0.0, -1.0]]]], dtype=torch.float64)
    out = F.conv2d(image, kernel)
    assert tuple(out.shape) == (1, 1, 2, 2)
    torch.testing.assert_close(out, torch.full_like(out, -4), atol=0, rtol=0)

    # Exercise 2: Rotate the kernel explicitly
    rotated = torch.flip(kernel, (-2, -1))
    changed = F.conv2d(image, rotated)
    torch.testing.assert_close(changed, torch.full_like(changed, 4), atol=0, rtol=0)

    # Exercise 3: Translate image layout
    nhwc = image.permute(0, 2, 3, 1)
    assert tuple(nhwc.shape) == (1, 3, 3, 1)
    assert torch.equal(nhwc.permute(0, 3, 1, 2), image)

    # Exercise 4: Inspect stride output size
    assert tuple(F.conv2d(image, kernel, stride=2).shape) == (1, 1, 1, 1)

    # Exercise 5: Trace one pixel influence
    perturbed = image.clone()
    perturbed[0, 0, 0, 0] += 10
    delta = F.conv2d(perturbed, kernel) - out
    torch.testing.assert_close(
        delta[0, 0], torch.tensor([[10.0, 0.0], [0.0, 0.0]], dtype=torch.float64), atol=0, rtol=0
    )

    # Exercise 6: Count shared parameters
    layer = nn.Conv2d(1, 2, 2, bias=False)
    assert sum(p.numel() for p in layer.parameters()) == 8
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
