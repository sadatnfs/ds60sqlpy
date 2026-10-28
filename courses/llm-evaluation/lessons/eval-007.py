import numpy as np


def bonferroni(pvalues, alpha=0.05):
    p = np.asarray(pvalues, float)
    if (
        not len(p)
        or np.any(p < 0)
        or np.any(p > 1)
        or not np.isfinite(p).all()
        or not 0 < alpha < 1
    ):
        raise ValueError("Invalid p-value family")
    return p <= alpha / len(p)


def spent_decisions(pvalues, budgets, alpha=0.05):
    p = np.asarray(pvalues, float)
    a = np.asarray(budgets, float)
    if (
        p.ndim != 1
        or p.shape != a.shape
        or not 0 < alpha < 1
        or not p.size
        or not np.isfinite(p).all()
        or not np.isfinite(a).all()
        or np.any(p < 0)
        or np.any(p > 1)
        or np.any(a < 0)
        or a.sum() > alpha + 1e-12
    ):
        raise ValueError("Invalid declared monitoring plan")
    return p <= a


def worked_a():
    unadjusted = 1 - (1 - 0.05) ** 3
    adjusted = 1 - (1 - 0.05 / 3) ** 3
    assert np.isclose(unadjusted, 0.142625) and adjusted < 0.05
    assert bonferroni([0.01, 0.03, 0.2]).tolist() == [True, False, False]
    print("Independent three-test family error:", unadjusted, "adjusted:", adjusted)


worked_a()

# Task 1: Test one valid p-value 0.05 at alpha 0.05.
# Task 2: Use p-values 0.02,0.02,0.02.
# Task 3: Allocate 0.03 and 0.03 while total alpha is 0.05.
# Task 4: Explain whether the union bound requires independent tests.
# Task 5: Replace a p-value with NaN.
# Task 6: A precise improvement is below the minimum useful effect.

# Implement your six changes below.
