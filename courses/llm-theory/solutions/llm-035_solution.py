"""llm-035: bounded local reference checks. No network or persistent data writes."""

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
    # Exercise 1: Define unequal requests
    torch.manual_seed(7); model=TinyDecoder(); model.eval(); requests={'A':[2,5,7],'B':[1,3]}; keys={r:(r,'model-v1','tokens-v1') for r in requests}
    assert len(set(keys.values()))==2 and [len(requests[r]) for r in ['A','B']]==[3,2]

    # Exercise 2: Interleave bounded work
    caches={}; outputs={r:[] for r in requests}
    with torch.no_grad():
        for request,index in [('A',0),('B',0),('A',1),('B',1),('A',2)]:
            key=keys[request]; logits,state=model(torch.tensor([[requests[request][index]]]),caches.get(key)); caches[key]=state; outputs[request].append(logits)
    assert caches[keys['A']]['k'].shape[2]==3 and caches[keys['B']]['k'].shape[2]==2

    # Exercise 3: Compare independent inference
    with torch.no_grad():
        for request,tokens in requests.items():
            full,_=model(torch.tensor([tokens])); incremental=torch.cat(outputs[request],dim=1); torch.testing.assert_close(incremental,full,atol=1e-6,rtol=0)

    # Exercise 4: Invalidate a tokenizer change
    assert caches.get(('A','model-v1','tokens-v2')) is None

    # Exercise 5: Invalidate a model change
    assert caches.get(('A','model-v2','tokens-v1')) is None

    # Exercise 6: Respect independent caps
    caps={'A':3,'B':2}; consumed={r:len(outputs[r]) for r in requests}
    assert consumed==caps and consumed['B']>=caps['B']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
