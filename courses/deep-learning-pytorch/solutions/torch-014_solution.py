"""torch-014: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Calculate uniform multiclass loss
    logits=torch.zeros((1,3),dtype=torch.float64); target=torch.tensor([1],dtype=torch.long)
    np.testing.assert_allclose(F.cross_entropy(logits,target).item(),np.log(3),atol=1e-12,rtol=0)

    # Exercise 2: Contrast independent binary outputs
    independent=torch.sigmoid(logits)
    assert independent.tolist()==[[.5,.5,.5]] and independent.sum().item()==1.5

    # Exercise 3: Inspect target shapes and types
    classes=torch.tensor([2,0],dtype=torch.long); labels=torch.tensor([[1.,0.,1.],[0.,1.,0.]])
    assert tuple(classes.shape)==(2,) and tuple(labels.shape)==(2,3) and classes.dtype==torch.long and labels.is_floating_point()

    # Exercise 4: Check class-axis normalization
    scores=torch.tensor([[2.,0.,-2.],[0.,1.,3.]])
    probs=torch.softmax(scores,dim=1); torch.testing.assert_close(probs.sum(1),torch.ones(2),atol=1e-6,rtol=0)

    # Exercise 5: Name the multilabel denominator
    per_entry=F.binary_cross_entropy_with_logits(torch.zeros_like(labels),labels,reduction='none')
    np.testing.assert_allclose([per_entry.sum().item(),per_entry.mean().item()],[6*np.log(2),np.log(2)],atol=1e-6,rtol=0)

    # Exercise 6: Reject an out-of-vocabulary class
    try: F.cross_entropy(torch.zeros((1,3)),torch.tensor([3]))
    except (IndexError,RuntimeError): pass
    else: raise AssertionError('unknown class accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
