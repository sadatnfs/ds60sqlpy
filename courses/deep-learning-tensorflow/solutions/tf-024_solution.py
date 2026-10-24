"""tf-024: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Freeze geometry and groups
    x = np.array([[-2.0], [-1.0], [1.0], [2.0]], dtype="float32")
    y = np.array([[0.0], [0.0], [1.0], [1.0]], dtype="float32")
    test_x = np.array([[-3.0], [3.0]], dtype="float32")
    test_y = np.array([0, 1])
    train_ids = {"a", "b", "c", "d"}
    test_ids = {"e", "f"}
    assert not train_ids & test_ids and len(test_ids) == 2

    # Exercise 2: Fit training preprocessing
    mean = x.mean(0)
    scale = x.std(0)
    tx = (x - mean) / scale
    vx = (test_x - mean) / scale
    np.testing.assert_allclose(scale, [np.sqrt(2.5)], atol=1e-6, rtol=0)
    assert mean[0] == 0 and vx[0, 0] == -vx[1, 0]

    # Exercise 3: Train within a fixed budget
    w = tf.Variable([[0.0]], dtype=tf.float32)
    for step in range(40):
        with tf.GradientTape() as tape:
            loss = tf.reduce_mean(
                tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=tf.constant(tx) @ w)
            )
        w.assign_sub(0.1 * tape.gradient(loss, w))
    assert step + 1 == 40 and float(w[0, 0]) > 0 and np.isfinite(w.numpy()).all()

    # Exercise 4: Account for every test row
    pred = (vx @ w.numpy()).ravel() >= 0
    truth = test_y.astype(bool)
    counts = {
        "tp": int(np.sum(pred & truth)),
        "tn": int(np.sum(~pred & ~truth)),
        "fp": int(np.sum(pred & ~truth)),
        "fn": int(np.sum(~pred & truth)),
    }
    assert counts == {"tp": 1, "tn": 1, "fp": 0, "fn": 0} and sum(counts.values()) == 2

    # Exercise 5: Compare a baseline
    baseline = np.zeros(2, dtype=bool)
    assert np.count_nonzero(baseline != truth) == 1 and np.count_nonzero(pred != truth) == 0

    # Exercise 6: Expose a subgroup failure
    broken = pred.copy()
    broken[1] = False
    report = {g: (int(broken[i] != truth[i]), 1) for i, g in enumerate(["negative", "positive"])}
    assert report == {"negative": (0, 1), "positive": (1, 1)}
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
