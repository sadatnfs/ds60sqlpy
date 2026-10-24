"""tf-012: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Freeze six records
    x = np.array(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1], [2, 1, 1]], dtype="float32"
    )
    y = x @ np.array([[2.0], [-1.0], [1.0]], dtype="float32")
    train = [0, 1, 2, 3]
    test = [4, 5]
    assert not set(train) & set(test)
    np.testing.assert_array_equal(y[:, 0], [0, 2, -1, 1, 2, 4])

    # Exercise 2: Measure the baseline
    mean = float(y[train].mean())
    baseline = float(np.mean((y[test] - mean) ** 2))
    assert mean == 0.5 and baseline == 7.25

    # Exercise 3: Train a bounded model
    w = tf.Variable(tf.zeros((3, 1)))
    tx = tf.constant(x[train])
    ty = tf.constant(y[train])
    initial = float(tf.reduce_mean(ty**2))
    for step in range(100):
        with tf.GradientTape() as tape:
            loss = tf.reduce_mean((tx @ w - ty) ** 2)
        w.assign_sub(0.1 * tape.gradient(loss, w))
    train_error = float(tf.reduce_mean((tx @ w - ty) ** 2))
    assert step + 1 == 100 and train_error < initial and np.isfinite(w.numpy()).all()

    # Exercise 4: Open the holdout once
    test_error = float(np.mean((x[test] @ w.numpy() - y[test]) ** 2))
    assert test_error < baseline
    report = {"train_mse": train_error, "test_mse": test_error, "test_count": 2, "steps": 100}
    assert report["test_count"] == 2

    # Exercise 5: Preserve arithmetic evidence
    pilot = np.array([1.0, 2.0, 3.0])
    gradient = 2 * np.mean((-2 * pilot) * pilot)
    updated = -0.1 * gradient
    np.testing.assert_allclose(
        [updated, np.mean((updated * pilot - 2 * pilot) ** 2)],
        [28 / 15, 56 / 675],
        atol=1e-12,
        rtol=0,
    )

    # Exercise 6: Reject a false conclusion
    report.update(
        train_ids=train,
        test_ids=test,
        limitation="Two synthetic holdout rows do not establish population reliability.",
    )
    assert report["test_ids"] == [4, 5] and "do not establish" in report["limitation"]
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
