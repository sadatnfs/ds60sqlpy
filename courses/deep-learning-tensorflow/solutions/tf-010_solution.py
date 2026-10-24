"""tf-010: bounded local reference checks. No network or persistent data writes."""

import numpy as np




def verify():
    # Exercise 1: Partition accounts
    groups=np.array(list('AABBCCDD')); x=np.array([1.,3.,5.,7.,20.,22.,30.,32.])
    train=np.isin(groups,['A','B']); valid=~train; mean=x[train].mean()
    assert mean==4 and set(groups[valid])=={'C','D'}

    # Exercise 2: Expose global fitting
    changed=x.copy(); changed[-1]=3200
    assert changed[train].mean()==mean
    assert changed.mean()!=x.mean()

    # Exercise 3: Find crossing groups
    wrong=np.arange(8)%2==0
    assert set(groups[wrong]) & set(groups[~wrong])==set('ABCD')

    # Exercise 4: Apply frozen centering
    np.testing.assert_array_equal(x[valid]-mean,[16,18,26,28])
    assert (x[train]-mean).mean()==0

    # Exercise 5: Freeze selection identity
    import hashlib,json
    ids=['a1','a2','b1','b2']; frozen=json.dumps(ids).encode(); digest=hashlib.sha256(frozen).hexdigest()
    validation_error=float(np.mean((x[valid]-mean)**2))
    assert validation_error>0 and hashlib.sha256(json.dumps(ids).encode()).hexdigest()==digest

    # Exercise 6: Transfer to unseen accounts
    new_value=1000-mean
    assert new_value==996 and mean==4
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
