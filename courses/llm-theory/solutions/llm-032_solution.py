"""llm-032: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Count adapter parameters
    w=torch.eye(8); a=nn.Parameter(torch.ones((8,2))/8); b=nn.Parameter(torch.zeros((2,8))); x=torch.ones((1,8))
    assert a.numel()+b.numel()==32 and w.numel()==64

    # Exercise 2: Check zero initial delta
    delta=a@b; initial=x@(w+delta)
    assert torch.equal(delta,torch.zeros((8,8))); assert torch.equal(initial,x@w)

    # Exercise 3: Differentiate the first objective
    saved=w.clone(); loss=initial.square().mean(); loss.backward()
    assert torch.count_nonzero(a.grad).item()==0 and torch.count_nonzero(b.grad).item()>0

    # Exercise 4: Update only the adapter
    before_b=b.detach().clone(); opt=torch.optim.SGD([a,b],lr=.1); opt.step()
    assert not torch.equal(b,before_b) and torch.equal(w,saved)

    # Exercise 5: Observe the changed function
    after=(x@(w+a@b)).square().mean()
    assert after.item()<loss.item()

    # Exercise 6: Bound the update rank
    assert int(torch.linalg.matrix_rank((a@b).detach()))<=2
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
