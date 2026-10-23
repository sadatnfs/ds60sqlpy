"""torch-005: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

def central(function,value,h):
    if not np.isfinite(h) or h<=0: raise ValueError('positive finite step required')
    left,right=function(value-h),function(value+h)
    if not np.isfinite([left,right]).all(): raise ValueError('finite probe values required')
    return (right-left)/(2*h)


def verify():
    # Exercise 1: Derive a scalar slope
    w=torch.tensor(0.,dtype=torch.float64,requires_grad=True); loss=(w-2)**2
    gradient=torch.autograd.grad(loss,w)[0]
    assert gradient.item()==-4 and loss.item()==4

    # Exercise 2: Check three finite differences
    for h in [.1,.01,.001]:
        slope=central(lambda value:(value-2)**2,0.,h)
        np.testing.assert_allclose(slope,-4,atol=1e-10,rtol=0)

    # Exercise 3: Separate gradient from update
    updated=0.-.1*gradient.item()
    np.testing.assert_allclose(updated,.4,atol=1e-12,rtol=0)
    assert updated!=gradient.item()

    # Exercise 4: Inspect a stationary point
    optimum=torch.tensor(2.,dtype=torch.float64,requires_grad=True)
    value=(optimum-2)**2; derivative=torch.autograd.grad(value,optimum)[0]
    assert value.item()==0 and derivative.item()==0

    # Exercise 5: Observe grad-return behavior
    assert w.grad is None and gradient.item()==-4

    # Exercise 6: Reject invalid probes
    for function,h in [(lambda x:x*x,0),(lambda x:x*x,-.1),(lambda x:float('inf'),.1)]:
        try: central(function,0.,h)
        except ValueError: pass
        else: raise AssertionError('invalid derivative probe accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
