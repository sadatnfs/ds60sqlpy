import numpy as np


def policy_metrics(scores, correct, threshold, wrong_cost=5.0, abstain_cost=0.4):
    p = np.asarray(scores, float)
    y = np.asarray(correct, float)
    if (
        p.shape != y.shape
        or not p.size
        or not np.isfinite(p).all()
        or np.any((p < 0) | (p > 1))
        or np.any((y != 0) & (y != 1))
        or not 0 <= threshold <= 1
    ):
        raise ValueError("Invalid selective evaluation")
    if not np.isfinite([wrong_cost, abstain_cost]).all() or wrong_cost < 0 or abstain_cost < 0:
        raise ValueError("Finite nonnegative costs required")
    answered = p >= threshold
    return {
        "coverage": float(answered.mean()),
        "accuracy": float(y[answered].mean()) if answered.any() else None,
        "cost": float(np.mean(np.where(answered, wrong_cost * (1 - y), abstain_cost))),
    }


def choose_threshold(scores, correct, thresholds):
    return min(thresholds, key=lambda t: (policy_metrics(scores, correct, t)["cost"], t))


def worked_a():
    scores = [0.9, 0.8, 0.4, 0.2]
    correct = [1, 0, 1, 0]
    threshold = choose_threshold(scores, correct, [0, 0.75, 0.85, 0.95])
    result = policy_metrics(scores, correct, threshold)
    assert threshold == 0.85 and result["coverage"] == 0.25 and result["accuracy"] == 1
    assert np.isclose(result["cost"], 0.3)
    assert np.isclose(1 - 0.4 / 5, 0.92)
    print("Development policy:", threshold, result)


worked_a()

# Task 1: Use threshold 0 on the development fixture.
# Task 2: Choose a threshold above every score.
# Task 3: Use score 0.5 and threshold 0.5.
# Task 4: Use wrong-answer cost 5 and abstention cost 0.4.
# Task 5: Compute the policy separately for routine and rare requests.
# Task 6: The held-out case exposes a bad threshold. What follows?

# Implement your six changes below.
