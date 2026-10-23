"""torch-010: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

class Accounts(torch.utils.data.Dataset):
    def __init__(self):
        self.groups=list('AABBCCDD'); self.values=torch.tensor([1.,3.,5.,7.,20.,22.,30.,32.],dtype=torch.float64)
    def __len__(self): return len(self.groups)
    def __getitem__(self,index): return index,self.groups[index],self.values[index]


def verify():
    # Exercise 1: Inspect a literal Dataset
    dataset=Accounts(); assert len(dataset)==8
    identity,group,value=dataset[0]; assert identity==0 and group=='A' and value.item()==1

    # Exercise 2: Select whole groups
    train_ids=[i for i in range(len(dataset)) if dataset[i][1] in {'A','B'}]; test_ids=[i for i in range(len(dataset)) if i not in train_ids]
    train=torch.utils.data.Subset(dataset,train_ids); test=torch.utils.data.Subset(dataset,test_ids)
    assert len(train)==len(test)==4 and not {row[1] for row in train}&{row[1] for row in test}

    # Exercise 3: Fit only training values
    mean=torch.stack([row[2] for row in train]).mean(); assert mean.item()==4

    # Exercise 4: Perturb only assessment values
    changed=Accounts(); changed.values=changed.values.clone(); changed.values[-1]=3200
    new_mean=torch.stack([changed[i][2] for i in train_ids]).mean()
    assert new_mean.item()==4 and changed.values.mean()!=dataset.values.mean()

    # Exercise 5: Expose row-level leakage
    left={dataset[i][1] for i in range(0,8,2)}; right={dataset[i][1] for i in range(1,8,2)}
    assert left&right==set('ABCD')

    # Exercise 6: Apply the frozen transform
    centered=torch.stack([row[2] for row in test])-mean
    torch.testing.assert_close(centered,torch.tensor([16.,18.,26.,28.],dtype=torch.float64),atol=0,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
