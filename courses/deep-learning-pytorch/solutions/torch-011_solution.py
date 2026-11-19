"""torch-011: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class ScalarModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
        self.register_buffer("offset", torch.tensor(0.0, dtype=torch.float64))

    def forward(self, x):
        return self.weight * x + self.offset


def verify():
    # Worked example A: Inspect module state
    model = ScalarModel()
    assert set(dict(model.named_parameters())) == {"weight"} and set(
        dict(model.named_buffers())
    ) == {"offset"}
    assert set(model.state_dict()) == {"weight", "offset"}

    # Worked example B: Check a forward call
    x = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    y = 2 * x
    assert torch.equal(model(x), torch.zeros_like(x)) and model.weight.item() == 0

    # Worked example C: Run one explicit loop step
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    optimizer.zero_grad(set_to_none=True)
    loss = ((model(x) - y) ** 2).mean()
    loss.backward()
    optimizer.step()
    np.testing.assert_allclose(model.weight.item(), 28 / 15, atol=1e-12, rtol=0)
    assert model.offset.item() == 0

    # Exercise 4: Move dtype through registered state
    model = model.to(dtype=torch.float32)
    assert model.weight.dtype == torch.float32 and model.offset.dtype == torch.float32

    # Exercise 5: Expose stale optimizer membership
    fresh = ScalarModel()
    old = fresh.weight
    stale = torch.optim.SGD(fresh.parameters(), lr=0.1)
    fresh.weight = nn.Parameter(torch.tensor(5.0, dtype=torch.float64))
    assert (
        stale.param_groups[0]["params"][0] is old
        and stale.param_groups[0]["params"][0] is not fresh.weight
    )

    # Exercise 6: Keep parameter count stable across calls
    stable = ScalarModel()
    identity = id(stable.weight)
    stable(torch.ones(1, dtype=torch.float64))
    stable(torch.ones(4, dtype=torch.float64))
    assert id(stable.weight) == identity and len(list(stable.parameters())) == 1

    # Exercise 1: Evaluate a module with a nonzero buffer
    shifted = ScalarModel()
    with torch.no_grad():
        shifted.offset.fill_(1.0)
    xs = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    assert shifted(xs).tolist() == [1.0, 1.0, 1.0] and "offset" not in dict(
        shifted.named_parameters()
    )

    # Exercise 2: Predict one step with the offset present
    optimizer2 = torch.optim.SGD(shifted.parameters(), lr=0.1)
    optimizer2.zero_grad(set_to_none=True)
    loss2 = ((shifted(xs) - 2 * xs) ** 2).mean()
    loss2.backward()
    optimizer2.step()
    np.testing.assert_allclose(loss2.item(), 35 / 3, atol=1e-12, rtol=0)
    np.testing.assert_allclose(shifted.weight.item(), 22 / 15, atol=1e-12, rtol=0)
    assert shifted.offset.item() == 1

    # Exercise 3: Count state in a ModuleList
    pair = nn.ModuleList([ScalarModel(), ScalarModel()])
    assert len(list(pair.parameters())) == 2 and len(list(pair.buffers())) == 2
    assert set(pair.state_dict()) == {"0.weight", "0.offset", "1.weight", "1.offset"}
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
