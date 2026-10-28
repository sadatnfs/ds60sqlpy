import numpy as np


def sigmoid(x):
    return np.exp(-np.logaddexp(0.0, -np.asarray(x, float)))


def pair_loss(scores):
    a, b = np.asarray(scores, float)
    return float(np.logaddexp(0.0, -(a - b)))


def pair_gradient(scores):
    a, b = np.asarray(scores, float)
    g = float(sigmoid(a - b) - 1)
    return np.array([g, -g])


def mle_difference(wins, losses):
    if not np.isfinite([wins, losses]).all() or wins <= 0 or losses <= 0:
        raise ValueError("Finite unregularized MLE needs wins and losses")
    return float(np.log(wins / losses))


def worked_a():
    scores = np.array([1.0, -1.0])
    shifted = scores + 100
    assert np.isclose(pair_loss(scores), pair_loss(shifted))
    analytic = pair_gradient(scores)
    h = 1e-5
    numeric = np.array(
        [
            (pair_loss(scores + np.eye(2)[i] * h) - pair_loss(scores - np.eye(2)[i] * h)) / (2 * h)
            for i in range(2)
        ]
    )
    np.testing.assert_allclose(analytic, numeric, rtol=1e-8, atol=1e-10)
    assert np.isclose(analytic.sum(), 0)
    print("Pair loss:", pair_loss(scores), "gradient:", analytic.tolist())


worked_a()

# Task 1: Evaluate a positive comparison when both scores are zero.
# Task 2: Add 100 to both responses.
# Task 3: Use one win and three losses.
# Task 4: Fit an unregularized pair with four wins and zero losses.
# Task 5: Use scores-1000 and 1000 for the preferred/rejected pair.
# Task 6: Observe A>B, B>C and C>A across labels.

# Implement your six changes below.
