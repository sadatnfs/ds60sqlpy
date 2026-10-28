from itertools import product

import numpy as np


def selection_optimism(candidates):
    if type(candidates) is not int or not 1 <= candidates <= 12:
        raise ValueError("Bounded candidate count required")
    return float(np.mean([max(noise) for noise in product((-0.1, 0.1), repeat=candidates)]))


def assess_procedure(development, assessment):
    dev = np.asarray(development, float)
    test = np.asarray(assessment, float)
    if (
        dev.ndim != 2
        or dev.shape != test.shape
        or not dev.size
        or not np.isfinite(dev).all()
        or not np.isfinite(test).all()
    ):
        raise ValueError("Aligned finite fold/candidate tables required")
    choices = np.argmax(dev, axis=1)
    selected = test[np.arange(len(choices)), choices]
    return choices, selected


def worked_a():
    values = [selection_optimism(n) for n in (1, 2, 4)]
    np.testing.assert_allclose(values, [0, 0.05, 0.0875], atol=1e-12)
    print("Mean selected development noise:", values)


worked_a()

# Task 1: Enumerate the four two-candidate noise combinations.
# Task 2: Alter the outer outcomes while retaining development scores.
# Task 3: Give equal development scores to two candidates.
# Task 4: Select using the outer table in case B.
# Task 5: Decide where a learned normalization or calibration fit belongs.
# Task 6: Use final-set errors to revise a prompt.

# Implement your six changes below.
