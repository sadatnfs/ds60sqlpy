"""torch-030: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Weight unequal shard means
    means=torch.tensor([2.,6.]); counts=torch.tensor([1.,3.])
    assert (means*counts).sum().div(counts.sum()).item()==5 and means.mean().item()==4

    # Exercise 2: Reconstruct an example mean
    values=torch.tensor([2.,4.,6.,8.]); parts=[values[:1],values[1:]]
    assert sum(part.sum() for part in parts).div(sum(part.numel() for part in parts)).item()==values.mean().item()==5

    # Exercise 3: Accumulate one full-batch gradient
    x=torch.arange(1,5,dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
    for start,end in [(0,1),(1,4)]: ((w*x[start:end]-y[start:end])**2).sum().backward()
    w.grad.div_(4)
    assert w.grad.item()==-30
    oracle=torch.tensor(0.,dtype=torch.float64,requires_grad=True); full=((oracle*x-y)**2).mean(); assert torch.autograd.grad(full,oracle)[0].item()==-30

    # Exercise 4: Apply one accumulated update
    torch.optim.SGD([w],lr=.01).step(); np.testing.assert_allclose(w.item(),.3,atol=1e-12,rtol=0)

    # Exercise 5: Contrast separate microbatch updates
    other=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); optimizer=torch.optim.SGD([other],lr=.01)
    for start,end in [(0,1),(1,4)]:
        optimizer.zero_grad(set_to_none=True); ((other*x[start:end]-y[start:end])**2).mean().backward(); optimizer.step()
    assert abs(other.item()-.3)>1e-6

    # Exercise 6: Represent empty-shard contributions
    empty=torch.empty(0); numerator=empty.sum()+values.sum(); denominator=empty.numel()+values.numel()
    assert denominator==4 and numerator.div(denominator).item()==5
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
