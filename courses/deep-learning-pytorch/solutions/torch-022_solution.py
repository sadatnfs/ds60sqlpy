"""torch-022: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

def attention(q,k,v,allowed):
    if any(value.ndim!=2 for value in (q,k,v)) or q.shape[0]==0 or q.shape[1]==0: raise ValueError('nonempty matrices required')
    if k.shape!=q.shape or v.shape[0]!=q.shape[0] or allowed.shape!=(q.shape[0],q.shape[0]): raise ValueError('shape mismatch')
    if allowed.dtype!=torch.bool: raise TypeError('boolean allowed mask required')
    if not bool(allowed.any(-1).all()) or not all(bool(torch.isfinite(value).all()) for value in (q,k,v)): raise ValueError('legal finite attention rows required')
    return F.scaled_dot_product_attention(q,k,v,attn_mask=allowed,dropout_p=0.)


def verify():
    # Exercise 1: Compute uniform causal mixtures
    q=torch.zeros((3,2),dtype=torch.float64); v=torch.tensor([[2.,0.],[0.,2.],[6.,6.]],dtype=torch.float64); allowed=torch.ones((3,3),dtype=torch.bool).tril()
    out=attention(q,q,v,allowed)
    torch.testing.assert_close(out,torch.tensor([[2.,0.],[1.,1.],[8/3,8/3]],dtype=torch.float64),atol=1e-12,rtol=0)

    # Exercise 2: Perturb only the future
    future=v.clone(); future[2]=torch.tensor([100.,200.]); changed=attention(q,q,future,allowed)
    torch.testing.assert_close(changed[:2],out[:2],atol=1e-12,rtol=0)
    torch.testing.assert_close(changed[2],torch.tensor([34.,202/3],dtype=torch.float64),atol=1e-12,rtol=0)

    # Exercise 3: Recompute nonuniform prefixes
    non=torch.tensor([[1.,0.],[0.,1.],[1.,1.]],dtype=torch.float64); full=attention(non,non,v,allowed)
    for cut in range(1,4): torch.testing.assert_close(attention(non[:cut],non[:cut],v[:cut],allowed[:cut,:cut]),full[:cut],atol=1e-12,rtol=0)

    # Exercise 4: Reject an all-masked row
    empty=allowed.clone(); empty[1]=False
    try: attention(q,q,v,empty)
    except ValueError: pass
    else: raise AssertionError('undefined row accepted')

    # Exercise 5: Translate mask polarity explicitly
    forbidden=~allowed
    assert forbidden[0].tolist()==[False,True,True]

    # Exercise 6: Keep inference dropout disabled
    again=attention(q,q,v,allowed)
    torch.testing.assert_close(again,out,atol=0,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
