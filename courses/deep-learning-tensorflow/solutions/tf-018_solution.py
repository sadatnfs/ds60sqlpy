"""tf-018: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Update moving state
    bn=tf.keras.layers.BatchNormalization(momentum=.5); x=tf.constant([[1.,3.],[3.,5.]])
    bn(x,training=True)
    np.testing.assert_allclose(bn.moving_mean.numpy(),[1,2],atol=1e-6,rtol=0)

    # Exercise 2: Freeze evaluation state
    before=bn.moving_mean.numpy().copy(); bn(tf.constant([[100.,200.]]),training=False)
    np.testing.assert_array_equal(before,bn.moving_mean.numpy())

    # Exercise 3: Test row independence
    ln=tf.keras.layers.LayerNormalization(axis=-1)
    a=ln(tf.constant([[1.,3.]])).numpy()[0]; b=ln(tf.constant([[1.,3.],[100.,200.]])).numpy()[0]
    np.testing.assert_allclose(a,b,atol=1e-6,rtol=0)

    # Exercise 4: Expose batch dependence
    small=np.array([[1.,3.],[3.,5.]]); large=np.vstack([small,[98.,199.]])
    np.testing.assert_array_equal(small[0]-small.mean(0),[-1,-1])
    np.testing.assert_array_equal(large[0]-large.mean(0),[-33,-66])

    # Exercise 5: Repeat the state update
    bn(x,training=True)
    np.testing.assert_allclose(bn.moving_mean.numpy(),[1.5,3],atol=1e-6,rtol=0)

    # Exercise 6: Handle a constant feature row
    constant=ln(tf.constant([[5.,5.]])).numpy()
    assert np.isfinite(constant).all(); np.testing.assert_allclose(constant,[[0,0]],atol=1e-6,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
