"""llm-040: bounded local reference checks. No network or persistent data writes."""

import numpy as np




def verify():
    # Exercise 1: Align paired question results
    families=['A','A','B']; diff=np.array([-1.,-1.,1.]); grouped=np.array([diff[np.array(families)==f].mean() for f in ['A','B']])
    np.testing.assert_array_equal(grouped,[-1,1]); np.testing.assert_allclose(diff.mean(),-1/3,atol=1e-12,rtol=0)

    # Exercise 2: Resample whole families
    indices=np.random.default_rng(8).integers(0,2,size=(1000,2)); estimates=grouped[indices].mean(1)
    assert set(np.unique(estimates))<={-1.,0.,1.} and grouped.mean()==0

    # Exercise 3: Expose row-weighting dependence
    repeated=np.concatenate([diff,[-1.]*10]); assert repeated.mean()!=diff.mean() and grouped.mean()==0

    # Exercise 4: Report selective accuracy
    total,answered,correct=4,2,2
    assert answered/total==.5 and correct/answered==1 and correct==2

    # Exercise 5: Audit decision chronology
    ledger=[('select_prompt','validation'),('assess','test')]
    assert all(part=='validation' for action,part in ledger if action=='select_prompt')
    forbidden=('select_prompt','test'); assert forbidden[1]!='validation'

    # Exercise 6: Combine gates with uncertainty
    gates={'severe_failures':1,'tested_families':2,'minimum_families':2}
    go=gates['severe_failures']==0 and gates['tested_families']>=gates['minimum_families']
    assert not go
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
