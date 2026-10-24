"""torch-034: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Count group errors
    truth=torch.tensor([1,1,0]); prediction=torch.tensor([1,0,0]); groups=['A','A','B']; errors=prediction!=truth
    report={group:(int(errors[torch.tensor([g==group for g in groups])].sum()),groups.count(group)) for group in ['A','B']}
    assert report=={'A':(1,2),'B':(0,1)}

    # Exercise 2: Expose repeated identities
    ids=['a','b','c']+['c']*5
    assert len(ids)==8 and len(set(ids))==3

    # Exercise 3: Trace a controlled perturbation
    base=torch.tensor(1.); shifts=torch.tensor([-.1,-.9,-1.1]); changed=(base+shifts>=0).long()
    assert changed.tolist()==[1,1,0]

    # Exercise 4: Keep severe failures visible
    passed=torch.tensor([True]*9+[False]); severe=torch.tensor([False]*9+[True])
    np.testing.assert_allclose(passed.float().mean().item(),.9,atol=1e-6,rtol=0)
    assert int((~passed&severe).sum())==1

    # Exercise 5: Represent an untested group
    def rate(errors,count): return None if count==0 else errors/count
    assert rate(0,0) is None and rate(0,1)==0

    # Exercise 6: Write a bounded card
    card={'unique_units':3,'use':'synthetic teaching','untested':['future population','private-data behavior'],'differential_privacy_established':False}
    assert card['unique_units']==3 and not card['differential_privacy_established']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
