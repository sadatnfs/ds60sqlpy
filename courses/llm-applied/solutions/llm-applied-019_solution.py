"""llm-applied-019: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Calculate the equal-margin loss
    difference=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); reference=0.; beta=.5
    loss=F.softplus(-beta*(difference-reference))
    np.testing.assert_allclose(loss.item(),np.log(2),atol=1e-12,rtol=0)

    # Exercise 2: Inspect the preference gradient
    loss.backward(); np.testing.assert_allclose(difference.grad.item(),-.25,atol=1e-12,rtol=0)

    # Exercise 3: Perform an actual update
    opt=torch.optim.SGD([difference],lr=.2); opt.step(); after=F.softplus(-beta*(difference-reference))
    np.testing.assert_allclose(difference.item(),.05,atol=1e-12,rtol=0); assert after.item()<loss.item()

    # Exercise 4: Reverse the preference
    reversed_difference=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); reversed_loss=F.softplus(beta*(reversed_difference-reference)); reversed_loss.backward()
    np.testing.assert_allclose(reversed_difference.grad.item(),.25,atol=1e-12,rtol=0)

    # Exercise 5: Separate objective and factual support
    answer={'preferred':True,'source_supported':False,'claim':'Conversion rate divides by all employees.'}
    assert answer['preferred'] and not answer['source_supported']

    # Exercise 6: Name the unexecuted RLHF machinery
    receipt={'offline_preference_update':True,'reward_model_trained':False,'online_rl':False,'production_alignment_established':False}
    assert receipt['offline_preference_update'] and not receipt['online_rl'] and not receipt['reward_model_trained']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
