"""tf-017: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Calculate penalties
    w=tf.constant([1.,-2.]); l1=float(tf.reduce_sum(tf.abs(w))); l2=float(tf.reduce_sum(w*w))
    assert (l1,l2)==(3.,5.)

    # Exercise 2: Switch dropout to evaluation
    layer=tf.keras.layers.Dropout(.5); x=tf.ones((4,8)); a=layer(x,training=False); b=layer(x,training=False)
    np.testing.assert_array_equal(a.numpy(),x.numpy()); np.testing.assert_array_equal(b.numpy(),x.numpy())

    # Exercise 3: Inspect training invariants
    train=layer(x,training=True).numpy()
    assert train.shape==(4,8) and set(np.unique(train))<={0.,2.}

    # Exercise 4: Separate objective terms
    data_loss=2.; coefficient=.1; penalty=coefficient*l2
    assert penalty==.5 and data_loss+penalty==2.5

    # Exercise 5: Differentiate the penalty
    v=tf.Variable([1.,-2.])
    with tf.GradientTape() as tape: penalty=.1*tf.reduce_sum(v*v)
    np.testing.assert_allclose(tape.gradient(penalty,v).numpy(),[.2,-.4],atol=1e-6,rtol=0)

    # Exercise 6: Scale weights deliberately
    assert float(tf.reduce_sum(tf.abs(2*w)))==6
    assert float(tf.reduce_sum((2*w)**2))==20
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
