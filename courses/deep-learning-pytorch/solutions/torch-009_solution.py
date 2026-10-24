"""torch-009: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Count batches and updates
    ids=list(range(1,7)); batches=[ids[i:i+2] for i in range(0,len(ids),2)]
    assert batches==[[1,2],[3,4],[5,6]]

    # Exercise 2: Retain a short tail
    short=[list(range(5))[i:i+2] for i in range(0,5,2)]
    assert [len(batch) for batch in short]==[2,2,1]

    # Exercise 3: Run three independent updates
    x=torch.arange(1,7,dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); optimizer=torch.optim.SGD([w],lr=.01); history=[]
    for start in range(0,6,2):
        optimizer.zero_grad(set_to_none=True); loss=((w*x[start:start+2]-y[start:start+2])**2).mean(); loss.backward(); optimizer.step(); history.append(w.item())
    assert len(history)==3 and np.isfinite(history).all() and len(set(history))==3

    # Exercise 4: Expose accidental accumulation
    bad=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); bad_optimizer=torch.optim.SGD([bad],lr=.01)
    for start in range(0,6,2):
        ((bad*x[start:start+2]-y[start:start+2])**2).mean().backward(); bad_optimizer.step()
    assert abs(bad.item()-history[-1])>1e-6

    # Exercise 5: Shuffle paired records together
    order=torch.tensor([5,0,4,1,3,2]); sx=x[order]; sy=y[order]
    torch.testing.assert_close(sy,2*sx,atol=0,rtol=0)

    # Exercise 6: Aggregate unequal batch means
    assert (2*2+8*1)/3==4 and (2+8)/2==5
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
