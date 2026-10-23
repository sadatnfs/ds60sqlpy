"""torch-018: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Update a running mean
    bn=nn.BatchNorm1d(2,momentum=.5); x=torch.tensor([[1.,3.],[3.,5.]])
    bn.train(); bn(x)
    torch.testing.assert_close(bn.running_mean,torch.tensor([1.,2.]),atol=1e-6,rtol=0); assert bn.num_batches_tracked.item()==1

    # Exercise 2: Freeze state during evaluation
    before=bn.running_mean.clone(); count=bn.num_batches_tracked.clone(); bn.eval(); bn(torch.tensor([[100.,200.]]))
    assert torch.equal(before,bn.running_mean) and torch.equal(count,bn.num_batches_tracked)

    # Exercise 3: Check LayerNorm row independence
    ln=nn.LayerNorm(2); alone=ln(torch.tensor([[1.,3.]])); together=ln(torch.tensor([[1.,3.],[100.,200.]]))
    torch.testing.assert_close(alone[0],together[0],atol=1e-6,rtol=0)

    # Exercise 4: Inspect running variance convention
    torch.testing.assert_close(bn.running_var,torch.tensor([1.5,1.5]),atol=1e-6,rtol=0)
    assert x.var(0,correction=0).tolist()==[1.,1.] and x.var(0,correction=1).tolist()==[2.,2.]

    # Exercise 5: Translate momentum explicitly
    old,batch=0.,10.; torch_update=(1-.1)*old+.1*batch; keras_update=.1*old+(1-.1)*batch
    assert torch_update==1 and keras_update==9

    # Exercise 6: Handle a constant feature row
    constant=ln(torch.tensor([[5.,5.]])); assert torch.isfinite(constant).all()
    torch.testing.assert_close(constant,torch.zeros((1,2)),atol=1e-6,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
