"""llm-019: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

class TinyDecoder(nn.Module):
    def __init__(self,vocab=16,width=32,heads=2,context=32):
        super().__init__()
        self.vocab,self.width,self.heads,self.context=vocab,width,heads,context
        self.token=nn.Embedding(vocab,width); self.position=nn.Embedding(context,width)
        self.norm1=nn.LayerNorm(width); self.qkv=nn.Linear(width,3*width,bias=False)
        self.projection=nn.Linear(width,width,bias=False); self.norm2=nn.LayerNorm(width)
        self.feed=nn.Sequential(nn.Linear(width,2*width),nn.ReLU(),nn.Linear(2*width,width))
        self.output=nn.Linear(width,vocab,bias=False)
    def forward(self,ids,cache=None):
        if ids.ndim!=2 or ids.dtype!=torch.long or ids.shape[1]==0: raise ValueError('nonempty long batch,time IDs')
        offset=0 if cache is None else cache['k'].shape[2]
        batch,time=ids.shape
        if offset+time>self.context or torch.any(ids<0) or torch.any(ids>=self.vocab): raise ValueError('context or vocabulary limit')
        x=self.token(ids)+self.position(torch.arange(offset,offset+time))
        q,k,v=self.qkv(self.norm1(x)).chunk(3,dim=-1)
        def split(t): return t.reshape(batch,time,self.heads,self.width//self.heads).transpose(1,2)
        q,k,v=map(split,(q,k,v))
        if cache is not None:
            if cache['k'].shape[0]!=batch: raise ValueError('cache batch mismatch')
            k=torch.cat([cache['k'],k],dim=2); v=torch.cat([cache['v'],v],dim=2)
        allowed=torch.arange(k.shape[2])[None,:]<=torch.arange(offset,offset+time)[:,None]
        scores=q@k.transpose(-2,-1)/(self.width//self.heads)**.5
        weights=torch.softmax(scores.masked_fill(~allowed,float('-inf')),dim=-1)
        mixed=(weights@v).transpose(1,2).contiguous().reshape(batch,time,self.width)
        x=x+self.projection(mixed); x=x+self.feed(self.norm2(x))
        return self.output(x),{'k':k.detach(),'v':v.detach()}


def verify():
    # Exercise 1: Clone the initial state
    torch.manual_seed(9); trained=TinyDecoder(); control=TinyDecoder(); control.load_state_dict(trained.state_dict())
    assert all(torch.equal(a,b) for a,b in zip(trained.parameters(),control.parameters()))
    x=torch.tensor([[1,2,3]]); y=torch.tensor([[2,3,4]])

    # Exercise 2: Run a no-update control
    before={k:v.clone() for k,v in control.state_dict().items()}; values=[]
    with torch.no_grad():
        for _ in range(5):
            z,_=control(x); values.append(F.cross_entropy(z.reshape(-1,16),y.reshape(-1)).item())
    assert len(set(values))==1 and all(torch.equal(v,before[k]) for k,v in control.state_dict().items())

    # Exercise 3: Train the repeated batch
    opt=torch.optim.Adam(trained.parameters(),lr=.02); curve=[]
    for _ in range(30):
        opt.zero_grad(set_to_none=True); z,_=trained(x); loss=F.cross_entropy(z.reshape(-1,16),y.reshape(-1)); curve.append(loss.item()); loss.backward(); opt.step()
    assert np.isfinite(curve).all() and curve[-1]<curve[0]

    # Exercise 4: Check the class axis
    z,_=trained(x); assert tuple(z.shape)==(1,3,16)

    # Exercise 5: Verify the control stayed isolated
    assert all(torch.equal(v,before[k]) for k,v in control.state_dict().items())

    # Exercise 6: Limit the conclusion
    report={'repeated_sequences':1,'updates':30,'heldout_count':0,'generalization_established':False}
    assert report['heldout_count']==0 and not report['generalization_established']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
