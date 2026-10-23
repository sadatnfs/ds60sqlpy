"""tf-031: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Check eager arithmetic
    x=tf.constant([1.,2.],tf.float32); eager=x*x+1
    np.testing.assert_array_equal(eager.numpy(),[2,5])

    # Exercise 2: Compile and compare
    @tf.function
    def f(value): return value*value+1
    np.testing.assert_array_equal(f(x).numpy(),eager.numpy()); first=f.experimental_get_tracing_count()
    assert first>=1

    # Exercise 3: Reuse an equal signature
    np.testing.assert_array_equal(f(tf.constant([3.,4.],tf.float32)).numpy(),[10,17])
    assert f.experimental_get_tracing_count()==first

    # Exercise 4: Change dtype deliberately
    out=f(tf.constant([1.,2.],tf.float64))
    assert out.dtype==tf.float64 and f.experimental_get_tracing_count()>first
    np.testing.assert_array_equal(out.numpy(),[2,5])

    # Exercise 5: Measure only warmed calls
    import time
    f(x).numpy(); start=time.perf_counter()
    for _ in range(10): result=f(x).numpy()
    elapsed=time.perf_counter()-start
    assert elapsed>=0 and np.isfinite(result).all()

    # Exercise 6: Separate shape contracts
    @tf.function(input_signature=[tf.TensorSpec([None],tf.float32)])
    def g(value): return value*value+1
    g(tf.constant([1.,2.])); count=g.experimental_get_tracing_count()
    assert tuple(g(tf.constant([1.,2.,3.])).shape)==(3,) and g.experimental_get_tracing_count()==count
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
