"""tf-027: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Construct the local base
    base=tf.keras.layers.Dense(2,use_bias=False,kernel_initializer=tf.keras.initializers.Identity()); x=tf.constant([[1.,0.],[0.,1.],[1.,1.]])
    base(x); base.trainable=False
    np.testing.assert_array_equal(base(x).numpy(),x.numpy()); assert not base.trainable_variables

    # Exercise 2: Train a new head
    head=tf.keras.layers.Dense(1,use_bias=False,kernel_initializer='zeros'); features=base(x,training=False); head(features); before=head.get_weights()[0].copy(); target=tf.constant([[1.],[2.],[3.]])
    with tf.GradientTape() as tape: loss=tf.reduce_mean((head(features)-target)**2)
    g=tape.gradient(loss,head.trainable_variables); tf.keras.optimizers.SGD(.1).apply_gradients(zip(g,head.trainable_variables))
    assert not np.array_equal(before,head.get_weights()[0])

    # Exercise 3: Prove base preservation
    np.testing.assert_array_equal(base.get_weights()[0],np.eye(2,dtype='float32'))

    # Exercise 4: Compare predictions
    pred=head(base(x,training=False)).numpy()
    assert pred.shape==(3,1) and (pred>0).all()

    # Exercise 5: Begin an explicit unfreeze phase
    base.trainable=True; variables=base.trainable_variables+head.trainable_variables
    with tf.GradientTape() as tape: loss=tf.reduce_mean((head(base(x,training=False))-target)**2)
    grads=tape.gradient(loss,variables)
    assert len(grads)==2 and all(g is not None for g in grads)
    tf.keras.optimizers.SGD(.01).apply_gradients(zip(grads,variables))

    # Exercise 6: Detect changed base state
    assert not np.array_equal(base.get_weights()[0],np.eye(2,dtype='float32'))
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
