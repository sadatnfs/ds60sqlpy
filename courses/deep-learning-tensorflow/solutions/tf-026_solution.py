"""tf-026: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf

class Residual(tf.keras.layers.Layer):
    def build(self,input_shape):
        self.width=int(input_shape[-1])
        self.kernel=self.add_weight(name='kernel',shape=(self.width,self.width),initializer='zeros')
    def call(self,x):
        if x.shape[-1]!=self.width: raise ValueError('feature width mismatch')
        return x+x@self.kernel


def verify():
    # Exercise 1: Create an identity residual
    layer=Residual(); x=tf.constant([[1.,2.],[3.,4.]]); out=layer(x)
    np.testing.assert_array_equal(out.numpy(),x.numpy()); assert len(layer.trainable_variables)==1

    # Exercise 2: Reuse the state
    variable=layer.trainable_variables[0]; layer(tf.constant([[9.,8.]]))
    assert layer.trainable_variables[0] is variable and len(layer.trainable_variables)==1

    # Exercise 3: Assign a known transform
    layer.kernel.assign(tf.eye(2)); np.testing.assert_array_equal(layer(x).numpy(),2*x.numpy())

    # Exercise 4: Reject an incompatible width
    try: layer(tf.ones((1,3)))
    except ValueError: pass
    else: raise AssertionError('width mismatch accepted')

    # Exercise 5: Check branch gradients
    with tf.GradientTape() as tape: total=tf.reduce_sum(layer(x))
    g=tape.gradient(total,layer.kernel)
    np.testing.assert_array_equal(g.numpy(),[[4,4],[6,6]])

    # Exercise 6: Count parameters by width
    other=Residual(); other(tf.ones((1,3)))
    assert other.count_params()==9 and layer.count_params()==4
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
