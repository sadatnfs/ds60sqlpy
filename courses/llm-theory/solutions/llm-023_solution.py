"""llm-023: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Retain the crossing token
    p = torch.tensor([0.5, 0.3, 0.2])
    sorted_p, order = torch.sort(p, descending=True, stable=True)
    previous = torch.cumsum(sorted_p, 0) - sorted_p
    keep = previous < 0.6
    assert order[keep].tolist() == [0, 1]
    np.testing.assert_allclose(sorted_p[keep].sum().item(), 0.8, atol=1e-6, rtol=0)

    # Exercise 2: Renormalize retained mass
    mass = sorted_p[keep]
    normalized = mass / mass.sum()
    np.testing.assert_allclose(normalized.numpy(), [0.625, 0.375], atol=1e-6, rtol=0)

    # Exercise 3: Reproduce local sampling
    g1 = torch.Generator().manual_seed(7)
    g2 = torch.Generator().manual_seed(7)
    a = torch.multinomial(normalized, 8, replacement=True, generator=g1)
    b = torch.multinomial(normalized, 8, replacement=True, generator=g2)
    assert torch.equal(a, b) and set(a.tolist()) <= {0, 1}

    # Exercise 4: Stop on EOS
    generated = []
    for token in [2, 3, 9, 4]:
        generated.append(token)
        if token == 9 or len(generated) >= 5:
            break
    assert generated == [2, 3, 9]

    # Exercise 5: Enforce a cap without EOS
    generated = []
    for _ in range(100):
        if len(generated) >= 3:
            break
        generated.append(2)
    assert generated == [2, 2, 2]

    # Exercise 6: Separate greedy mode
    logits = torch.tensor([2.0, 1.0, 0.0])
    temperature = 0
    choice = int(logits.argmax()) if temperature == 0 else -1
    assert choice == 0 and torch.isfinite(logits).all()
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
