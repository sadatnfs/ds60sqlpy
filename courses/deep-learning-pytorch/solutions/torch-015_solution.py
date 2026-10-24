"""torch-015: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def collate(sequences):
    if not sequences or any(len(sequence) == 0 for sequence in sequences):
        raise ValueError("nonempty sequences required")
    if any(
        isinstance(token, (bool, np.bool_))
        or not isinstance(token, (int, np.integer))
        or not 0 <= int(token) < 2**63
        for sequence in sequences
        for token in sequence
    ):
        raise ValueError("nonnegative int64 token IDs required")
    lengths = torch.tensor([len(sequence) for sequence in sequences], dtype=torch.long)
    batch = torch.zeros((len(sequences), int(lengths.max())), dtype=torch.long)
    for row, sequence in enumerate(sequences):
        batch[row, : len(sequence)] = torch.tensor(sequence)
    return batch, lengths


def verify():
    # Exercise 1: Inspect retained batches
    dataset = torch.utils.data.TensorDataset(
        torch.arange(5), torch.arange(1, 6, dtype=torch.float32)
    )
    loader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=False, num_workers=0)
    batches = list(loader)
    assert [len(ids) for ids, values in batches] == [2, 2, 1]
    assert torch.cat([ids for ids, values in batches]).tolist() == [0, 1, 2, 3, 4]

    # Exercise 2: Make dropping explicit
    dropped = list(
        torch.utils.data.DataLoader(dataset, batch_size=2, drop_last=True, num_workers=0)
    )
    assert len(dropped) == 2 and torch.cat([ids for ids, values in dropped]).tolist() == [
        0,
        1,
        2,
        3,
    ]

    # Exercise 3: Reproduce shuffle with a local generator
    def order(seed):
        generator = torch.Generator().manual_seed(seed)
        batches = torch.utils.data.DataLoader(
            dataset, batch_size=2, shuffle=True, generator=generator, num_workers=0
        )
        return torch.cat([ids for ids, values in batches]).tolist()

    assert order(7) == order(7) and sorted(order(7)) == list(range(5))

    # Exercise 4: Collate variable-length sequences
    padded, lengths = collate([[2, 3], [4]])
    assert padded.tolist() == [[2, 3], [4, 0]] and lengths.tolist() == [2, 1]

    # Exercise 5: Preserve pairing after shuffle
    paired = torch.utils.data.TensorDataset(torch.arange(6), 2 * torch.arange(6))
    for ids, targets in torch.utils.data.DataLoader(
        paired,
        batch_size=2,
        shuffle=True,
        generator=torch.Generator().manual_seed(9),
        num_workers=0,
    ):
        assert torch.equal(targets, 2 * ids)

    # Exercise 6: Reject invalid sequence records
    try:
        collate([[], [1]])
    except ValueError:
        pass
    else:
        raise AssertionError("empty sequence accepted")
    for invalid in [[[2.7]], [[True]], [[-1]], [[2**63]]]:
        try:
            collate(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid token ID accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
