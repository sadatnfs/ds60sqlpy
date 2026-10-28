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


def worked_a():
    assert np.isclose(dpo_loss(0, 0, 2), np.log(2))
    assert dpo_gradient(0, 0, 2) == -1
    delta = 0.4
    h = 1e-5
    numeric = (dpo_loss(delta + h, 0, 2) - dpo_loss(delta - h, 0, 2)) / (2 * h)
    assert np.isclose(numeric, dpo_gradient(delta, 0, 2), atol=1e-10)
    print("Reference loss:", dpo_loss(0, 0, 2), "initial gradient:", dpo_gradient(0, 0, 2))


worked_a()

# Task 1: Set policy and reference log odds equal for any positive beta.
# Task 2: Use beta 2 and zero reference-relative log-odds shift.
# Task 3: Fit a3:1 preference ratio with beta 0.5,1 and 2 under a uniform reference.
# Task 4: Use the token log-ratio arrays in the reference exercise.
# Task 5: Update the reference parameters while retaining the same loss label.
# Task 6: Observe a lower training DPO loss.

# Implement your six changes below.
