"""torch-025: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Compare dot and cosine scores
    anchor = torch.tensor([1.0, 0.0], dtype=torch.float64)
    positive = torch.tensor([1.0, 1.0], dtype=torch.float64)
    negative = torch.tensor([0.0, 1.0], dtype=torch.float64)
    assert torch.dot(anchor, positive).item() == 1 and torch.dot(anchor, negative).item() == 0
    np.testing.assert_allclose(
        F.cosine_similarity(anchor, positive, dim=0).item(), 1 / np.sqrt(2), atol=1e-12, rtol=0
    )

    # Exercise 2: Scale without changing direction
    scaled = 10 * positive
    assert torch.dot(anchor, scaled).item() == 10
    torch.testing.assert_close(
        F.cosine_similarity(anchor, scaled, dim=0),
        F.cosine_similarity(anchor, positive, dim=0),
        atol=1e-12,
        rtol=0,
    )

    # Exercise 3: Calculate a two-candidate loss
    logits = torch.tensor([[1.0, 0.0]], dtype=torch.float64)
    np.testing.assert_allclose(
        F.cross_entropy(logits, torch.tensor([0])).item(), np.log1p(np.exp(-1)), atol=1e-12, rtol=0
    )

    # Exercise 4: Inspect a projection gradient
    projection = nn.Parameter(torch.eye(2, dtype=torch.float64))
    query = anchor @ projection
    scores = torch.stack([query @ positive, query @ negative])[None, :]
    F.cross_entropy(scores, torch.tensor([0])).backward()
    assert (
        projection.grad is not None
        and torch.isfinite(projection.grad).all()
        and torch.count_nonzero(projection.grad) > 0
    )

    # Exercise 5: Detect contradictory candidate identity
    pair = {"positive": "doc-a", "negative": "doc-a"}
    assert pair["positive"] == pair["negative"]

    # Exercise 6: Separate temperature from ranking
    warm = torch.softmax(logits, dim=1)
    cool = torch.softmax(logits / 0.5, dim=1)
    assert cool[0, 0] > warm[0, 0] and warm.argmax(1).item() == cool.argmax(1).item() == 0
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
