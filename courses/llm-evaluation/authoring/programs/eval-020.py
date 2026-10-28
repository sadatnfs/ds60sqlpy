import numpy as np


def sigmoid(x):
    return np.exp(-np.logaddexp(0.0, -np.asarray(x, float)))


def dpo_loss(delta, reference_delta, beta=1.0, win_fraction=1.0):
    if (
        not np.isfinite([delta, reference_delta, beta, win_fraction]).all()
        or beta <= 0
        or not 0 <= win_fraction <= 1
    ):
        raise ValueError("Positive beta and valid frequency required")
    z = beta * (delta - reference_delta)
    return float(win_fraction * np.logaddexp(0.0, -z) + (1 - win_fraction) * np.logaddexp(0.0, z))


def dpo_gradient(delta, reference_delta, beta=1.0, win_fraction=1.0):
    dpo_loss(delta, reference_delta, beta, win_fraction)
    return float(beta * (sigmoid(beta * (delta - reference_delta)) - win_fraction))


def fitted_delta(wins, losses, beta, reference_delta=0.0):
    if (
        not np.isfinite([wins, losses, beta, reference_delta]).all()
        or wins <= 0
        or losses <= 0
        or beta <= 0
    ):
        raise ValueError("Finite preference fit requires both labels")
    return reference_delta + np.log(wins / losses) / beta


# === EXAMPLE A ===
def worked_a():
    assert np.isclose(dpo_loss(0, 0, 2), np.log(2))
    assert dpo_gradient(0, 0, 2) == -1
    delta = 0.4
    h = 1e-5
    numeric = (dpo_loss(delta + h, 0, 2) - dpo_loss(delta - h, 0, 2)) / (2 * h)
    assert np.isclose(numeric, dpo_gradient(delta, 0, 2), atol=1e-10)
    print("Reference loss:", dpo_loss(0, 0, 2), "initial gradient:", dpo_gradient(0, 0, 2))


# === EXAMPLE B ===
def worked_b():
    deltas = [fitted_delta(3, 1, beta) for beta in (0.5, 1.0, 2.0)]
    probabilities = sigmoid(deltas)
    np.testing.assert_allclose(probabilities, [0.9, 0.75, np.sqrt(3) / (1 + np.sqrt(3))])
    assert all(
        abs(dpo_gradient(delta, 0, beta, 0.75)) < 1e-12
        for delta, beta in zip(deltas, (0.5, 1.0, 2.0), strict=True)
    )
    print("Policy probabilities at empirical optima:", probabilities.tolist())


# === EXERCISES ===
def exercise_checks():
    assert np.isclose(dpo_loss(3, 3, 0.1), np.log(2))
    assert np.isfinite(dpo_loss(-1000, 0, 2))
    assert fitted_delta(2, 2, 1) == 0
    chosen = np.array([-0.1, -0.1]) - np.array([-0.4, -0.4])
    rejected = np.array([-0.1] * 4) - np.array([-0.3] * 4)
    assert chosen.sum() - rejected.sum() < 0
    assert chosen.mean() - rejected.mean() > 0
    try:
        fitted_delta(4, 0, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Separable fit given finite optimum")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-020: all reference checks passed")


if __name__ == "__main__":
    main()
