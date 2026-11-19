"""torch-021: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Lookup and mark padding
    table = torch.tensor([[0.0, 0.0], [1.0, 0.0], [2.0, 2.0], [3.0, -1.0]])
    embedding = nn.Embedding.from_pretrained(table, freeze=False, padding_idx=0)
    ids = torch.tensor([[2, 3, 0]])
    values = embedding(ids)
    mask = ids != 0
    assert tuple(values.shape) == (1, 3, 2) and mask.tolist() == [[True, True, False]]

    # Worked example B: Verify padding-row gradient behavior
    values.sum().backward()
    assert torch.count_nonzero(embedding.weight.grad[0]).item() == 0
    assert torch.count_nonzero(embedding.weight.grad[2:4]).item() > 0

    # Worked example C: Compare packed and valid-prefix GRU state
    gru = nn.GRU(2, 2, batch_first=True)
    with torch.no_grad():
        for parameter in gru.parameters():
            parameter.fill_(0.1)
    packed = nn.utils.rnn.pack_padded_sequence(
        values.detach(), torch.tensor([2]), batch_first=True, enforce_sorted=False
    )
    _, packed_state = gru(packed)
    _, prefix_state = gru(values.detach()[:, :2])
    torch.testing.assert_close(packed_state, prefix_state, atol=1e-6, rtol=0)

    # Exercise 4: Expose an unmasked recurrent tail
    _, padded_state = gru(values.detach())
    assert not torch.allclose(padded_state, prefix_state, atol=1e-6, rtol=0)

    # Exercise 5: Average only valid token losses
    losses = torch.tensor([[np.log(2), np.log(2), 100.0]], dtype=torch.float64)
    mean = losses[mask].mean()
    np.testing.assert_allclose(mean.item(), np.log(2), atol=1e-12, rtol=0)

    # Exercise 6: Reject zero-length recurrent input
    try:
        nn.utils.rnn.pack_padded_sequence(
            values.detach(), torch.tensor([0]), batch_first=True, enforce_sorted=False
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("zero-length packed sequence accepted")

    # Exercise 1: Look up a short sequence
    lookup_table = torch.tensor([[0.0, 0.0], [1.0, 0.0], [2.0, 2.0], [3.0, -1.0]])
    lookup = nn.Embedding.from_pretrained(lookup_table, freeze=False, padding_idx=0)
    short_ids = torch.tensor([[1, 0, 0]])
    short_values = lookup(short_ids)
    assert short_values.tolist() == [[[1.0, 0.0], [0.0, 0.0], [0.0, 0.0]]] and (
        short_ids != 0
    ).tolist() == [[True, False, False]]

    # Exercise 2: Count gradients for repeated IDs
    lookup(torch.tensor([[2, 2, 3]])).sum().backward()
    assert lookup.weight.grad.tolist() == [[0.0, 0.0], [0.0, 0.0], [2.0, 2.0], [1.0, 1.0]]

    # Exercise 3: Pack a batch with two lengths
    rnn = nn.GRU(2, 2, batch_first=True)
    with torch.no_grad():
        for weight in rnn.parameters():
            weight.fill_(0.1)
    batch = torch.tensor([[[1.0, 0.0], [2.0, 2.0]], [[3.0, -1.0], [0.0, 0.0]]])
    packed_batch = nn.utils.rnn.pack_padded_sequence(
        batch, torch.tensor([2, 1]), batch_first=True, enforce_sorted=False
    )
    _, states = rnn(packed_batch)
    _, first = rnn(batch[:1, :2])
    _, second = rnn(batch[1:, :1])
    torch.testing.assert_close(states[:, 0], first[:, 0], atol=1e-6, rtol=0)
    torch.testing.assert_close(states[:, 1], second[:, 0], atol=1e-6, rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
