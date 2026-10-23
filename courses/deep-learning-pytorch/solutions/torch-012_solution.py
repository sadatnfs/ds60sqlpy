"""torch-012: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Create the three-feature fixture
    x=torch.tensor([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[1.,1.,1.],[2.,1.,1.]],dtype=torch.float64)
    y=x@torch.tensor([[2.],[-1.],[1.]],dtype=torch.float64); train=[0,1,2,3]; test=[4,5]
    torch.testing.assert_close(y[:,0],torch.tensor([0.,2.,-1.,1.,2.,4.],dtype=torch.float64),atol=0,rtol=0)

    # Exercise 2: Measure the training-mean baseline
    mean=y[train].mean(); baseline=((y[test]-mean)**2).mean()
    assert mean.item()==.5 and baseline.item()==7.25

    # Exercise 3: Train a bounded linear model
    model=nn.Linear(3,1,bias=False,dtype=torch.float64)
    with torch.no_grad(): model.weight.zero_()
    optimizer=torch.optim.SGD(model.parameters(),lr=.1); initial=((model(x[train])-y[train])**2).mean().item(); curve=[]
    for _ in range(100):
        optimizer.zero_grad(set_to_none=True); loss=((model(x[train])-y[train])**2).mean(); curve.append(loss.item()); loss.backward(); optimizer.step()
    assert len(curve)==100 and np.isfinite(curve).all() and curve[-1]<initial

    # Exercise 4: Open the holdout after fitting
    model.eval()
    with torch.no_grad(): train_error=((model(x[train])-y[train])**2).mean().item(); test_error=((model(x[test])-y[test])**2).mean().item()
    assert np.isfinite([train_error,test_error]).all() and test_error<baseline.item()

    # Exercise 5: Retain an independent pilot oracle
    pilot=np.array([1.,2.,3.]); gradient=2*np.mean((-2*pilot)*pilot); updated=-.1*gradient
    np.testing.assert_allclose([updated,np.mean((updated*pilot-2*pilot)**2)],[28/15,56/675],atol=1e-12,rtol=0)

    # Exercise 6: Write the bounded evidence report
    report={'train_ids':train,'test_ids':test,'steps':100,'train_mse':train_error,'test_mse':test_error,'limit':'two synthetic holdout rows'}
    assert not set(train)&set(test) and len(report['test_ids'])==2 and report['steps']==100
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
