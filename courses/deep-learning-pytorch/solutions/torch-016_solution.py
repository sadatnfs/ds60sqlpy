"""torch-016: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Construct XOR by hand
    x=torch.tensor([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
    w=torch.tensor([[1.,-1.],[-1.,1.]])
    h=F.relu(x@w); output=h.sum(1)
    assert output.tolist()==[0.,1.,1.,0.]

    # Exercise 2: Remove the nonlinearity
    assert (x@w).sum(1).tolist()==[0.,0.,0.,0.]

    # Exercise 3: Map the construction into Linear
    layer=nn.Linear(2,2,bias=False)
    with torch.no_grad(): layer.weight.copy_(w.T)
    torch.testing.assert_close(F.relu(layer(x)),h,atol=0,rtol=0)

    # Exercise 4: Inspect activation gradients
    z=torch.tensor([-2.,2.],requires_grad=True); F.relu(z).sum().backward()
    assert z.grad.tolist()==[0.,1.]

    # Exercise 5: Expose identical-unit symmetry
    symmetric=nn.Linear(2,2,bias=False)
    with torch.no_grad(): symmetric.weight.copy_(torch.tensor([[1.,2.],[1.,2.]]))
    features=symmetric(x); torch.testing.assert_close(features[:,0],features[:,1],atol=0,rtol=0)

    # Exercise 6: Transfer to continuous inputs
    points=torch.tensor([[.2,.8],[.8,.2]])
    torch.testing.assert_close(F.relu(points@w).sum(1),torch.tensor([.6,.6]),atol=1e-6,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
