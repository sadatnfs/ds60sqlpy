"""llm-027: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Exercise 1: Weight token losses
    means = np.array([1.0, 3.0])
    counts = np.array([1, 3])
    assert np.average(means, weights=counts) == 2.5 and means.mean() == 2

    # Exercise 2: Build a calibration bin
    confidence = np.array([0.6, 0.8, 0.8, 1.0])
    correct = np.array([1, 1, 0, 1])
    assert len(confidence) == 4
    np.testing.assert_allclose(confidence.mean(), 0.8, atol=1e-12, rtol=0)
    assert correct.mean() == 0.75

    # Exercise 3: Represent an empty bin
    mask = confidence < 0.5
    summary = {
        "count": int(mask.sum()),
        "accuracy": None if not mask.any() else float(correct[mask].mean()),
    }
    assert summary == {"count": 0, "accuracy": None}

    # Exercise 4: Check boundary membership
    low = (confidence >= 0.5) & (confidence < 0.8)
    high = (confidence >= 0.8) & (confidence <= 1)
    assert (int(low.sum()), int(high.sum())) == (1, 3) and int((low | high).sum()) == 4

    # Exercise 5: Align paired errors
    a = {"q1": 0, "q2": 1}
    b = {"q2": 0, "q1": 1}
    ids = sorted(a)
    diff = np.array([a[i] - b[i] for i in ids])
    np.testing.assert_array_equal(diff, [-1, 1])
    assert diff.mean() == 0

    # Exercise 6: Reject incompatible tokenizer scores
    left = {"tokenizer": "v1", "unit": "token"}
    right = {"tokenizer": "v2", "unit": "token"}
    assert left != right
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
