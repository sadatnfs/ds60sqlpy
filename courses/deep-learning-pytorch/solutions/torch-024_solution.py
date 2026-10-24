"""torch-024: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Freeze the geometric task
    x=torch.tensor([[-2.],[-1.],[1.],[2.]]); y=torch.tensor([[0.],[0.],[1.],[1.]])
    test_x=torch.tensor([[-3.],[3.]]); truth=torch.tensor([False,True]); train_ids={'a','b','c','d'}; test_ids={'e','f'}
    assert not train_ids&test_ids and len(test_ids)==2

    # Exercise 2: Fit explicit normalization
    mean=x.mean(0); scale=x.std(0,correction=0); tx=(x-mean)/scale; vx=(test_x-mean)/scale
    assert mean.item()==0; np.testing.assert_allclose(scale.item(),np.sqrt(2.5),atol=1e-6,rtol=0)

    # Exercise 3: Train a fixed classifier
    model=nn.Linear(1,1,bias=False)
    with torch.no_grad(): model.weight.zero_()
    optimizer=torch.optim.SGD(model.parameters(),lr=.1)
    for _ in range(40):
        optimizer.zero_grad(set_to_none=True); loss=F.binary_cross_entropy_with_logits(model(tx),y); loss.backward(); optimizer.step()
    assert model.weight.item()>0 and torch.isfinite(model.weight).all()

    # Exercise 4: Account for every test prediction
    model.eval()
    with torch.no_grad(): prediction=model(vx).ravel()>=0
    counts={'tp':int((prediction&truth).sum()),'tn':int((~prediction&~truth).sum()),'fp':int((prediction&~truth).sum()),'fn':int((~prediction&truth).sum())}
    assert counts=={'tp':1,'tn':1,'fp':0,'fn':0} and sum(counts.values())==2

    # Exercise 5: Compare a constant baseline
    baseline=torch.zeros(2,dtype=torch.bool)
    assert int((baseline!=truth).sum())==1 and int((prediction!=truth).sum())==0

    # Exercise 6: Reveal a group-specific failure
    broken=prediction.clone(); broken[1]=False
    report={group:(int(broken[i]!=truth[i]),1) for i,group in enumerate(['negative','positive'])}
    assert report=={'negative':(0,1),'positive':(1,1)}
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
