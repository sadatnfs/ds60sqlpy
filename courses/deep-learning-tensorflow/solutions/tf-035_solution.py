"""tf-035: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Worked example A: Align by identity
    truth = {"a": 0.0, "b": 1.0, "c": 2.0}
    a = {"a": 0.0, "b": 2.0, "c": 2.0}
    b = {"c": 3.0, "a": 1.0, "b": 2.0}
    ids = sorted(truth)
    diff = np.array([(a[i] - truth[i]) ** 2 - (b[i] - truth[i]) ** 2 for i in ids])
    np.testing.assert_array_equal(diff, [-1, 0, -1])

    # Worked example B: Calculate the mean difference
    np.testing.assert_allclose(diff.mean(), -2 / 3, atol=1e-12, rtol=0)

    # Exercise 3: Resample paired units
    rng = np.random.default_rng(7)
    indices = rng.integers(0, len(diff), size=(1000, len(diff)))
    estimates = diff[indices].mean(1)
    assert (
        estimates.shape == (1000,)
        and np.isfinite(estimates).all()
        and estimates.min() >= -1
        and estimates.max() <= 0
    )

    # Exercise 4: Reproduce the resampling
    again = np.random.default_rng(7).integers(0, 3, size=(1000, 3))
    np.testing.assert_array_equal(diff[again].mean(1), estimates)

    # Exercise 5: Refuse mismatched IDs
    missing = {k: v for k, v in b.items() if k != "c"}
    assert set(missing) != set(truth)

    # Exercise 6: Keep selection and final evaluation separate
    ledger = [
        {"action": "choose", "partition": "validation"},
        {"action": "assess", "partition": "test"},
    ]
    assert all(row["partition"] == "validation" for row in ledger if row["action"] == "choose")
    bad = {"action": "choose", "partition": "test"}
    assert bad["partition"] != "validation"

    # Exercise 1: Align a fourth record
    truth4 = {"a": 0.0, "b": 1.0, "c": 2.0, "d": 4.0}
    a4 = {"d": 5.0, "a": 0.0, "b": 2.0, "c": 2.0}
    b4 = {"b": 1.0, "d": 4.0, "c": 3.0, "a": 1.0}
    diff4 = np.array([(a4[i] - truth4[i]) ** 2 - (b4[i] - truth4[i]) ** 2 for i in sorted(truth4)])
    np.testing.assert_array_equal(diff4, [-1, 1, -1, 1])
    assert diff4.mean() == 0

    # Exercise 2: Expose positional pairing
    positional = np.array(
        [(pa - t) ** 2 - (pb - t) ** 2 for t, pa, pb in zip(truth.values(), a.values(), b.values())]
    )
    np.testing.assert_array_equal(positional, [-9, 1, 0])
    assert not np.array_equal(positional, diff)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
