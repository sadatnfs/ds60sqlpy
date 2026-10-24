"""tf-029: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Expose naive overflow
    z=np.array([1000.,999.])
    with np.errstate(over='ignore'): naive=np.exp(z)
    assert np.isinf(naive).all()

    # Exercise 2: Calculate stable loss
    loss=tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0],logits=tf.constant([[1000.,999.]]))
    np.testing.assert_allclose(loss.numpy(),[np.logaddexp(0,-1)],atol=1e-6,rtol=0)

    # Exercise 3: Check shift invariance
    np.testing.assert_allclose(tf.nn.softmax(z).numpy(),tf.nn.softmax([0.,-1.]).numpy(),atol=1e-6,rtol=0)

    # Exercise 4: Inspect gradients
    v=tf.Variable([[1000.,999.]])
    with tf.GradientTape() as tape: objective=tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0],logits=v))
    g=tape.gradient(objective,v).numpy()
    assert np.isfinite(g).all(); np.testing.assert_allclose(g.sum(),0,atol=1e-6,rtol=0)

    # Exercise 5: Separate precision policies
    with np.errstate(over='ignore'): low=np.exp(np.float16(20))
    high=np.exp(np.float64(20))
    assert np.isinf(low) and np.isfinite(high)

    # Exercise 6: Validate input finiteness
    def stable(values):
        values=np.asarray(values,dtype=float)
        if values.ndim!=1 or not len(values) or not np.isfinite(values).all(): raise ValueError('finite vector')
        mass=np.exp(values-values.max()); return mass/mass.sum()
    try: stable([0,np.nan])
    except ValueError: pass
    else: raise AssertionError('NaN accepted')
    np.testing.assert_allclose(stable(z).sum(),1,atol=1e-12,rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
