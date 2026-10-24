"""tf-031: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Check eager arithmetic
    x = tf.constant([1., 2.], dtype=tf.float32)
    eager = x * x + 1
    np.testing.assert_array_equal(eager.numpy(), [2, 5])

    # Exercise 2: Trace a graph and compare
    @tf.function
    def f(value):
        return value * value + 1

    np.testing.assert_array_equal(f(x).numpy(), eager.numpy())
    first = f.experimental_get_tracing_count()
    assert first >= 1

    # Exercise 3: Reuse an equal signature
    same_signature = tf.constant([3., 4.], dtype=tf.float32)
    np.testing.assert_array_equal(f(same_signature).numpy(), [10, 17])
    assert f.experimental_get_tracing_count() == first

    # Exercise 4: Change dtype deliberately
    different_dtype = tf.constant([1., 2.], dtype=tf.float64)
    output = f(different_dtype)
    assert output.dtype == tf.float64
    assert f.experimental_get_tracing_count() > first
    np.testing.assert_array_equal(output.numpy(), [2, 5])

    # Exercise 5: Measure only warmed calls
    import time

    f(x).numpy()
    start = time.perf_counter()
    observations = [f(x).numpy() for _ in range(10)]
    elapsed = time.perf_counter() - start
    assert len(observations) == 10
    assert elapsed >= 0
    for observed in observations:
        assert np.isfinite(observed).all()
        np.testing.assert_array_equal(observed, [2, 5])

    # Exercise 6: Separate shape contracts
    @tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
    def g(value):
        return value * value + 1

    g(tf.constant([1., 2.], dtype=tf.float32))
    count = g.experimental_get_tracing_count()
    output = g(tf.constant([1., 2., 3.], dtype=tf.float32))
    assert tuple(output.shape) == (3,)
    assert g.experimental_get_tracing_count() == count
    for incompatible in [tf.constant([[1., 2.]], dtype=tf.float32), tf.constant([1., 2.], dtype=tf.float64)]:
        try:
            g(incompatible)
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError('incompatible signature accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
