"""tf-016: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Construct XOR
    x=tf.constant([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
    w=tf.constant([[1.,-1.],[-1.,1.]])
    h=tf.nn.relu(x@w); output=tf.reduce_sum(h,axis=1)
    np.testing.assert_array_equal(output.numpy(),[0,1,1,0])

    # Exercise 2: Remove the nonlinearity
    np.testing.assert_array_equal(tf.reduce_sum(x@w,axis=1).numpy(),[0,0,0,0])

    # Exercise 3: Compose affine matrices
    a=tf.constant([[1.,2.],[3.,4.]]); b=tf.constant([[2.],[-1.]])
    np.testing.assert_allclose(((x@a)@b).numpy(),(x@(a@b)).numpy(),atol=1e-6,rtol=0)

    # Exercise 4: Inspect a dead region
    z=tf.Variable([-2.,2.])
    with tf.GradientTape() as tape: total=tf.reduce_sum(tf.nn.relu(z))
    np.testing.assert_array_equal(tf.nn.relu(z).numpy(),[0,2]); np.testing.assert_array_equal(tape.gradient(total,z).numpy(),[0,1])

    # Exercise 5: Show symmetry
    same=tf.constant([[1.,1.],[2.,2.]])
    features=tf.nn.relu(x@same).numpy(); np.testing.assert_array_equal(features[:,0],features[:,1])

    # Exercise 6: Transfer outside the corners
    q=tf.constant([[.2,.8],[.8,.2]])
    np.testing.assert_allclose(tf.reduce_sum(tf.nn.relu(q@w),axis=1).numpy(),[.6,.6],atol=1e-6,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
