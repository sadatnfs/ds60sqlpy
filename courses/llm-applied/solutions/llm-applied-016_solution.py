"""llm-applied-016: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Count and orient parameters
    w=torch.eye(8); a=nn.Parameter(torch.ones((8,2))/8); b=nn.Parameter(torch.zeros((2,8))); rank=2; alpha=4; scale=alpha/rank; x=torch.ones((1,8))
    assert w.numel()==64 and a.numel()+b.numel()==32 and scale==2

    # Exercise 2: Prove zero-delta initialization
    initial=x@(w+scale*(a@b)); saved=w.clone()
    assert torch.equal(initial,x@w) and torch.equal(a@b,torch.zeros((8,8)))

    # Exercise 3: Inspect the first gradients
    loss=initial.square().mean(); loss.backward()
    assert torch.count_nonzero(a.grad).item()==0 and torch.count_nonzero(b.grad).item()>0 and w.grad is None

    # Exercise 4: Take an adapter-only step
    before_b=b.detach().clone(); opt=torch.optim.SGD([a,b],lr=.1); opt.step(); after=x@(w+scale*(a@b))
    assert not torch.equal(before_b,b) and after.square().mean()<loss and torch.equal(w,saved)

    # Exercise 5: Merge without changing the base
    merged=w.detach().clone()+scale*(a@b).detach()
    torch.testing.assert_close(x@merged,after.detach(),atol=1e-6,rtol=0)
    assert torch.equal(w,saved)

    # Exercise 6: Inspect rank and scaling consequences
    delta=(a@b).detach(); assert int(torch.linalg.matrix_rank(delta))<=2
    torch.testing.assert_close((4/rank)*delta,2*((2/rank)*delta),atol=1e-6,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
