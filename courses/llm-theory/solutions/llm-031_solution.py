"""llm-031: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Align the target mask
    sequence=torch.tensor([[1,2,5,6,3]]); targets=sequence[:,1:]; answer=torch.tensor([[False,True,True,True]])
    assert targets.tolist()==[[2,5,6,3]] and int(answer.sum())==3

    # Exercise 2: Compute answer-only loss
    logits=torch.zeros((1,4,8)); masked=targets.masked_fill(~answer,-100)
    loss=F.cross_entropy(logits.reshape(-1,8),masked.reshape(-1),ignore_index=-100)
    np.testing.assert_allclose(loss.item(),np.log(8),atol=1e-6,rtol=0)

    # Exercise 3: Compare loss sums
    full=F.cross_entropy(logits.reshape(-1,8),targets.reshape(-1),reduction='sum')
    answer_sum=F.cross_entropy(logits.reshape(-1,8),masked.reshape(-1),ignore_index=-100,reduction='sum')
    np.testing.assert_allclose([full.item(),answer_sum.item()],[4*np.log(8),3*np.log(8)],atol=1e-6,rtol=0)

    # Exercise 4: Inspect ignored gradients
    v=logits.clone().requires_grad_(); F.cross_entropy(v.reshape(-1,8),masked.reshape(-1),ignore_index=-100).backward()
    assert torch.count_nonzero(v.grad[:,0]).item()==0 and torch.count_nonzero(v.grad[:,1:]).item()>0

    # Exercise 5: Detect template leakage
    family={'p1':'T','p2':'T'}; assert {family['p1']} & {family['p2']}=={'T'}

    # Exercise 6: Refuse missing answers
    empty=torch.zeros((1,4),dtype=torch.bool)
    try:
        if int(empty.sum())==0: raise ValueError('answer targets required')
    except ValueError: pass
    else: raise AssertionError('empty answer accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
