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


# === EXAMPLE A ===
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


# === EXAMPLE B ===
def worked_b():
    delta = mle_difference(3, 1)
    assert np.isclose(sigmoid(delta), 0.75)
    # Strict scalar inequalities a>b, b>c, c>a cannot all hold.
    a, b, c = 2.0, 1.0, 0.0
    assert (a > b) and (b > c) and not (c > a)
    print("Pairwise MLE difference:", delta, "probability:", float(sigmoid(delta)))


# === EXERCISES ===
def exercise_checks():
    assert np.isclose(pair_loss([0, 0]), np.log(2))
    assert np.isfinite(pair_loss([-1000, 1000])) and pair_loss([-1000, 1000]) == 2000
    assert np.isclose(sigmoid(mle_difference(1, 3)), 0.25)
    assert np.isclose(mle_difference(2, 2), 0)
    try:
        mle_difference(4, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Infinite MLE represented as finite")
    np.testing.assert_allclose(pair_gradient([4, 2]), pair_gradient([104, 102]))


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-017: all reference checks passed")


if __name__ == "__main__":
    main()
