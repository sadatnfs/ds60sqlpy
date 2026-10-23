"""torch-007: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Inspect leaf and nonleaf state
    w=torch.tensor(0.,requires_grad=True); intermediate=2*w; intermediate.retain_grad(); intermediate.backward()
    assert w.is_leaf and not intermediate.is_leaf and w.grad.item()==2 and intermediate.grad.item()==1

    # Exercise 2: Observe accumulation across fresh graphs
    w.grad=None; ((w-2)**2).backward(); assert w.grad.item()==-4
    ((w-2)**2).backward(); assert w.grad.item()==-8

    # Exercise 3: Clear before an independent step
    w.grad=None; ((w-2)**2).backward(); assert w.grad.item()==-4

    # Exercise 4: Separate detach from ownership
    source=torch.tensor([1.,2.],requires_grad=True); detached=source.detach(); owned=source.detach().clone(); detached[0]=9
    assert source[0].item()==9 and owned[0].item()==1 and not detached.requires_grad

    # Exercise 5: Use no_grad for an observation
    value=torch.tensor(2.,requires_grad=True); tracked=value*3
    with torch.no_grad(): observed=value*3
    assert tracked.requires_grad and not observed.requires_grad

    # Exercise 6: Show eval is separate
    model=nn.Linear(1,1); model.eval(); result=model(torch.tensor([[1.]],requires_grad=True))
    assert result.requires_grad and model.training is False
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
