"""torch-011: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

class ScalarModel(nn.Module):
    def __init__(self):
        super().__init__(); self.weight=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); self.register_buffer('offset',torch.tensor(0.,dtype=torch.float64))
    def forward(self,x): return self.weight*x+self.offset


def verify():
    # Exercise 1: Inspect module state
    model=ScalarModel()
    assert set(dict(model.named_parameters()))=={'weight'} and set(dict(model.named_buffers()))=={'offset'}
    assert set(model.state_dict())=={'weight','offset'}

    # Exercise 2: Check a forward call
    x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x
    assert torch.equal(model(x),torch.zeros_like(x)) and model.weight.item()==0

    # Exercise 3: Run one explicit loop step
    optimizer=torch.optim.SGD(model.parameters(),lr=.1); optimizer.zero_grad(set_to_none=True)
    loss=((model(x)-y)**2).mean(); loss.backward(); optimizer.step()
    np.testing.assert_allclose(model.weight.item(),28/15,atol=1e-12,rtol=0); assert model.offset.item()==0

    # Exercise 4: Move dtype through registered state
    model=model.to(dtype=torch.float32)
    assert model.weight.dtype==torch.float32 and model.offset.dtype==torch.float32

    # Exercise 5: Expose stale optimizer membership
    fresh=ScalarModel(); old=fresh.weight; stale=torch.optim.SGD(fresh.parameters(),lr=.1); fresh.weight=nn.Parameter(torch.tensor(5.,dtype=torch.float64))
    assert stale.param_groups[0]['params'][0] is old and stale.param_groups[0]['params'][0] is not fresh.weight

    # Exercise 6: Keep parameter count stable across calls
    stable=ScalarModel(); identity=id(stable.weight); stable(torch.ones(1,dtype=torch.float64)); stable(torch.ones(4,dtype=torch.float64))
    assert id(stable.weight)==identity and len(list(stable.parameters()))==1
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
