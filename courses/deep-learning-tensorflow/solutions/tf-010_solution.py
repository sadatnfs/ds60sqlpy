"""tf-010: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Worked example A: Partition accounts
    groups = np.array(list("AABBCCDD"))
    x = np.array([1.0, 3.0, 5.0, 7.0, 20.0, 22.0, 30.0, 32.0])
    train = np.isin(groups, ["A", "B"])
    valid = ~train
    mean = x[train].mean()
    assert mean == 4 and set(groups[valid]) == {"C", "D"}

    # Worked example B: Expose global fitting
    changed = x.copy()
    changed[-1] = 3200
    assert changed[train].mean() == mean
    assert changed.mean() != x.mean()

    # Exercise 3: Find crossing groups
    wrong = np.arange(8) % 2 == 0
    assert set(groups[wrong]) & set(groups[~wrong]) == set("ABCD")

    # Exercise 4: Apply frozen centering
    np.testing.assert_array_equal(x[valid] - mean, [16, 18, 26, 28])
    assert (x[train] - mean).mean() == 0

    # Exercise 5: Freeze selection identity
    import hashlib, json

    ids = ["a1", "a2", "b1", "b2"]
    frozen = json.dumps(ids).encode()
    digest = hashlib.sha256(frozen).hexdigest()
    validation_error = float(np.mean((x[valid] - mean) ** 2))
    assert validation_error > 0 and hashlib.sha256(json.dumps(ids).encode()).hexdigest() == digest

    # Exercise 6: Transfer to unseen accounts
    new_value = 1000 - mean
    assert new_value == 996 and mean == 4

    # Exercise 1: Partition a second account fixture
    groups2 = np.array(list("EEFFGGHH"))
    x2 = np.array([2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 40.0, 44.0])
    train2 = np.isin(groups2, ["E", "F", "G"])
    mean2 = x2[train2].mean()
    assert mean2 == 7 and set(groups2[~train2]) == {"H"}
    np.testing.assert_array_equal(x2[~train2] - mean2, [33.0, 37.0])

    # Exercise 2: Predict the effect of a training outlier
    outlier = x2.copy()
    outlier[0] = 200
    shifted = outlier[train2].mean()
    assert shifted == 40
    np.testing.assert_array_equal(outlier[~train2] - shifted, [0.0, 4.0])
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
