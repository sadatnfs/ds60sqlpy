"""llm-026: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Construct transparent representations
    features=torch.tensor([[-2.,0.],[-1.,1.],[1.,0.],[2.,1.]]); labels=torch.tensor([0,0,1,1]); prediction=(features[:,0]>0).long()
    assert torch.equal(prediction,labels)

    # Exercise 2: Use a held-out fixture
    held=torch.tensor([[-3.,1.],[3.,0.]]); truth=torch.tensor([0,1]); got=(held[:,0]>0).long()
    assert torch.equal(got,truth)

    # Exercise 3: Add shuffled-label control
    shuffled=torch.tensor([0,1,0,1]); assert int((prediction==shuffled).sum())==2

    # Exercise 4: Protect frozen state
    before=features.clone(); weight=nn.Parameter(torch.tensor([[1.],[0.]])); logits=(features@weight).ravel(); loss=F.binary_cross_entropy_with_logits(logits,labels.float()); loss.backward()
    assert weight.grad is not None and features.grad is None and torch.equal(features,before)

    # Exercise 5: Expose family leakage
    families=['A','A','B','C']; assert {families[0]} & {families[1]}=={'A'}

    # Exercise 6: Bound the interpretation
    report={'heldout_count':2,'control_accuracy':.5,'decodable':True,'causal_use_established':False}
    assert report['decodable'] and not report['causal_use_established']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
