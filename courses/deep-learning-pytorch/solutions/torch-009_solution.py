"""torch-009: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Count batches and updates
    ids = list(range(1, 7))
    batches = [ids[i : i + 2] for i in range(0, len(ids), 2)]
    assert batches == [[1, 2], [3, 4], [5, 6]]

    # Worked example B: Retain a short tail
    short = [list(range(5))[i : i + 2] for i in range(0, 5, 2)]
    assert [len(batch) for batch in short] == [2, 2, 1]

    # Worked example C: Run three independent updates
    x = torch.arange(1, 7, dtype=torch.float64)
    y = 2 * x
    w = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
    optimizer = torch.optim.SGD([w], lr=0.01)
    history = []
    for start in range(0, 6, 2):
        optimizer.zero_grad(set_to_none=True)
        loss = ((w * x[start : start + 2] - y[start : start + 2]) ** 2).mean()
        loss.backward()
        optimizer.step()
        history.append(w.item())
    assert len(history) == 3 and np.isfinite(history).all() and len(set(history)) == 3

    # Exercise 4: Expose accidental accumulation
    bad = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
    bad_optimizer = torch.optim.SGD([bad], lr=0.01)
    for start in range(0, 6, 2):
        ((bad * x[start : start + 2] - y[start : start + 2]) ** 2).mean().backward()
        bad_optimizer.step()
    assert abs(bad.item() - history[-1]) > 1e-6

    # Exercise 5: Shuffle paired records together
    order = torch.tensor([5, 0, 4, 1, 3, 2])
    sx = x[order]
    sy = y[order]
    torch.testing.assert_close(sy, 2 * sx, atol=0, rtol=0)

    # Exercise 6: Aggregate unequal batch means
    assert (2 * 2 + 8 * 1) / 3 == 4 and (2 + 8) / 2 == 5

    # Exercise 1: Partition with batch size 4
    ten = list(range(1, 11))
    quads = [ten[i : i + 4] for i in range(0, len(ten), 4)]
    assert [len(batch) for batch in quads] == [4, 4, 2] and quads[-1] == [9, 10]

    # Exercise 2: Count updates with a dropped tail
    steps_per_epoch = len(ten) // 4
    assert (
        steps_per_epoch == 2
        and 3 * steps_per_epoch == 6
        and [i for batch in quads[:steps_per_epoch] for i in batch] == list(range(1, 9))
    )

    # Exercise 3: Trace two single-record updates
    pair_x = torch.tensor([1.0, 2.0], dtype=torch.float64)
    pair_y = 2 * pair_x
    weight = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
    opt = torch.optim.SGD([weight], lr=0.1)
    trace = []
    for index in range(2):
        opt.zero_grad(set_to_none=True)
        ((weight * pair_x[index] - pair_y[index]) ** 2).backward()
        opt.step()
        trace.append(weight.item())
    np.testing.assert_allclose(trace, [0.4, 1.68], atol=1e-12, rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
