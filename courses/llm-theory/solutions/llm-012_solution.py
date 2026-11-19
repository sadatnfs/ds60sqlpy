"""llm-012: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def softmax(x):
    x = np.asarray(x, dtype=float)
    mass = np.exp(x - x.max())
    return mass / mass.sum()


def verify():
    # Worked example A: Calculate greedy choice
    scores = np.array([2.0, 1.0, 0.0])
    assert int(np.argmax(scores)) == 0

    # Worked example B: Change temperature
    p = softmax(scores)
    cool = softmax(scores / 0.5)
    assert cool[0] > p[0] and p.argmax() == cool.argmax() == 0

    # Exercise 3: Use fixed draws
    mass = np.array([0.5, 0.3, 0.2])
    cumulative = np.cumsum(mass)
    assert [int(np.searchsorted(cumulative, d, side="right")) for d in [0.1, 0.6, 0.9]] == [0, 1, 2]

    # Exercise 4: Retain two candidates
    allowed = np.argsort(-scores, kind="stable")[:2]
    filtered = np.zeros(3)
    filtered[allowed] = softmax(scores[allowed])
    assert filtered[2] == 0
    np.testing.assert_allclose(filtered.sum(), 1, atol=1e-12, rtol=0)

    # Exercise 5: Declare ties
    assert int(np.argmax([1, 1, 0])) == 0

    # Exercise 6: Reject invalid draws
    def validate_draw(draw):
        if not np.isfinite(draw) or not 0 <= draw < 1:
            raise ValueError("draw in [0,1)")
        return draw

    assert validate_draw(0) == 0 and validate_draw(0.999) == 0.999
    for bad in [1, -0.1]:
        try:
            validate_draw(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid draw")

    # Exercise 1: Predict a hotter distribution
    scores2 = np.array([0.5, 3.0, 3.5, -1.0])
    base = softmax(scores2)
    hot = softmax(scores2 / 2)
    assert int(np.argmax(scores2)) == 2 and base.argmax() == hot.argmax() == 2
    assert hot[2] < base[2] and hot[3] > base[3]

    # Exercise 2: Compute an exact two-token probability
    pair = softmax([1.0, 0.0])
    sharp = softmax(np.array([1.0, 0.0]) / 0.5)
    np.testing.assert_allclose(pair[0], 1 / (1 + np.exp(-1)), atol=1e-12, rtol=0)
    np.testing.assert_allclose(sharp[0], 1 / (1 + np.exp(-2)), atol=1e-12, rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
