"""llm-applied-013: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Exercise 1: Align paired errors
    a = {"q1": 0, "q2": 0, "q3": 1}
    b = {"q3": 0, "q1": 1, "q2": 1}
    ids = sorted(a)
    assert set(a) == set(b)
    difference = np.array([a[i] - b[i] for i in ids], dtype=float)
    np.testing.assert_array_equal(difference, [-1, -1, 1])

    # Exercise 2: Aggregate by family
    families = np.array(["F", "F", "G"])
    family_values = np.array([difference[families == f].mean() for f in ["F", "G"]])
    np.testing.assert_allclose(difference.mean(), -1 / 3, atol=1e-12, rtol=0)
    assert family_values.mean() == 0

    # Exercise 3: Resample paired families
    indices = np.random.default_rng(17).integers(0, 2, size=(2000, 2))
    estimates = family_values[indices].mean(1)
    assert set(np.unique(estimates)) == {-1.0, 0.0, 1.0}
    np.testing.assert_array_equal(indices, np.random.default_rng(17).integers(0, 2, size=(2000, 2)))

    # Exercise 4: Report coverage and answered accuracy
    total, answered, correct = 10, 6, 5
    assert answered / total == 0.6 and correct / answered == 5 / 6 and total - answered == 4

    # Exercise 5: Block a severe boundary failure
    mean_gain = 0.1
    access_leaks = 1
    release = mean_gain > 0 and access_leaks == 0
    assert not release

    # Exercise 6: Keep final tests out of selection
    ledger = [("choose_k", "validation"), ("score_final", "test")]
    assert all(part == "validation" for action, part in ledger if action == "choose_k")
    assert ("choose_k", "test")[1] != "validation"
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
