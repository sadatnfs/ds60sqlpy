"""tf-009: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Count updates
    ids=list(range(1,7)); batches=[ids[i:i+2] for i in range(0,6,2)]
    assert batches==[[1,2],[3,4],[5,6]]

    # Exercise 2: Retain a remainder
    ids=list(range(1,6)); batches=[ids[i:i+2] for i in range(0,5,2)]
    assert list(map(len,batches))==[2,2,1]
    assert sum((b for b in batches if len(b)==2),[])==[1,2,3,4]

    # Exercise 3: Trace weight state
    x=tf.constant([1.,2.,3.,4.,5.,6.]); y=2*x; w=tf.Variable(0.); history=[]
    for i in range(0,6,2):
        with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x[i:i+2]-y[i:i+2])**2)
        w.assign_sub(.01*tape.gradient(loss,w)); history.append(float(w))
    assert len(history)==3 and all(np.isfinite(history))
    assert len(set(history))==3

    # Exercise 4: Compare batch policies
    def train(size):
        w=tf.Variable(0.); steps=0
        for i in range(0,6,size):
            with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x[i:i+size]-y[i:i+size])**2)
            w.assign_sub(.01*tape.gradient(loss,w)); steps+=1
        return float(w),steps
    a,na=train(1); b,nb=train(3)
    assert (na,nb)==(6,2) and abs(a-b)>1e-6

    # Exercise 5: Preserve pairs
    order=tf.constant([5,0,4,1,3,2]); sx=tf.gather(x,order); sy=tf.gather(y,order)
    np.testing.assert_allclose(sy.numpy(),2*sx.numpy())
    assert not np.allclose(y.numpy(),2*sx.numpy())

    # Exercise 6: Aggregate unequal batches
    assert (2*2+8*1)/3==4
    assert (2+8)/2==5
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
