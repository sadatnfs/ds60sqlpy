import numpy as np


def target_mean(means, weights):
    if set(means) != set(weights) or not means:
        raise ValueError("Every target stratum needs data")
    w = np.array(list(weights.values()), float)
    if not np.isfinite(np.asarray(list(means.values()), float)).all():
        raise ValueError("Finite stratum means required")
    if np.any(w < 0) or not np.isfinite(w).all() or not np.isclose(w.sum(), 1):
        raise ValueError("Invalid population weights")
    return sum(weights[h] * means[h] for h in weights)


def inclusion_estimates(y, probability, population_size):
    y = np.asarray(y, float)
    p = np.asarray(probability, float)
    if (
        y.shape != p.shape
        or not y.size
        or np.any(p <= 0)
        or np.any(p > 1)
        or not np.isfinite(p).all()
        or population_size <= 0
    ):
        raise ValueError("Invalid inclusion design")
    weights = 1 / p
    return (
        float(np.sum(weights * y) / population_size),
        float(np.sum(weights * y) / weights.sum()),
        float(weights.sum() ** 2 / np.sum(weights**2)),
    )


def worked_a():
    means = {"routine": 0.9, "rare": 0.5}
    estimate = target_mean(means, {"routine": 0.9, "rare": 0.1})
    assert np.isclose(estimate, 0.86)
    assert np.isclose(target_mean(means, {"routine": 0.5, "rare": 0.5}), 0.7)
    print("Target estimate:", estimate, "balanced sample mean:", 0.7)


worked_a()

# Task 1: Use 25% routine and 75% rare in case A.
# Task 2: Give positive target weight to an unobserved stratum.
# Task 3: Explain why the two weighted means in case B differ.
# Task 4: Use inclusion probabilities 0.01 and 1.
# Task 5: Set one inclusion probability to zero.
# Task 6: Use a common family/stratum ledger to compare A and B.

# Implement your six changes below.
