"""torch-010: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class Accounts(torch.utils.data.Dataset):
    def __init__(self):
        self.groups = list("AABBCCDD")
        self.values = torch.tensor(
            [1.0, 3.0, 5.0, 7.0, 20.0, 22.0, 30.0, 32.0], dtype=torch.float64
        )

    def __len__(self):
        return len(self.groups)

    def __getitem__(self, index):
        return index, self.groups[index], self.values[index]


def verify():
    # Worked example A: Inspect a literal Dataset
    dataset = Accounts()
    assert len(dataset) == 8
    identity, group, value = dataset[0]
    assert identity == 0 and group == "A" and value.item() == 1

    # Worked example B: Select whole groups
    train_ids = [i for i in range(len(dataset)) if dataset[i][1] in {"A", "B"}]
    test_ids = [i for i in range(len(dataset)) if i not in train_ids]
    train = torch.utils.data.Subset(dataset, train_ids)
    test = torch.utils.data.Subset(dataset, test_ids)
    assert len(train) == len(test) == 4 and not {row[1] for row in train} & {row[1] for row in test}

    # Worked example C: Fit only training values
    mean = torch.stack([row[2] for row in train]).mean()
    assert mean.item() == 4

    # Exercise 4: Perturb only assessment values
    changed = Accounts()
    changed.values = changed.values.clone()
    changed.values[-1] = 3200
    new_mean = torch.stack([changed[i][2] for i in train_ids]).mean()
    assert new_mean.item() == 4 and changed.values.mean() != dataset.values.mean()

    # Exercise 5: Expose row-level leakage
    left = {dataset[i][1] for i in range(0, 8, 2)}
    right = {dataset[i][1] for i in range(1, 8, 2)}
    assert left & right == set("ABCD")

    # Exercise 6: Apply the frozen transform
    centered = torch.stack([row[2] for row in test]) - mean
    torch.testing.assert_close(
        centered, torch.tensor([16.0, 18.0, 26.0, 28.0], dtype=torch.float64), atol=0, rtol=0
    )

    # Exercise 1: Inspect a different record
    record = Accounts()[5]
    assert record[0] == 5 and record[1] == "C" and record[2].item() == 22

    # Exercise 2: Hold out a different pair of groups
    pool = Accounts()
    keep = [i for i in range(len(pool)) if pool[i][1] in {"A", "C"}]
    rest = [i for i in range(len(pool)) if i not in keep]
    fit = torch.utils.data.Subset(pool, keep)
    held = torch.utils.data.Subset(pool, rest)
    assert {row[1] for row in fit} == {"A", "C"} and not {row[1] for row in fit} & {
        row[1] for row in held
    }
    assert torch.stack([row[2] for row in fit]).mean().item() == 11.5

    # Exercise 3: Apply the new frozen transform
    shifted_values = torch.stack([row[2] for row in held]) - 11.5
    torch.testing.assert_close(
        shifted_values, torch.tensor([-6.5, -4.5, 18.5, 20.5], dtype=torch.float64), atol=0, rtol=0
    )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
