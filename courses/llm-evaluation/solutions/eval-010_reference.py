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


# === EXAMPLE A ===
def worked_a():
    scores = [0.9, 0.8, 0.4, 0.2]
    correct = [1, 0, 1, 0]
    threshold = choose_threshold(scores, correct, [0, 0.75, 0.85, 0.95])
    result = policy_metrics(scores, correct, threshold)
    assert threshold == 0.85 and result["coverage"] == 0.25 and result["accuracy"] == 1
    assert np.isclose(result["cost"], 0.3)
    assert np.isclose(1 - 0.4 / 5, 0.92)
    print("Development policy:", threshold, result)


# === EXAMPLE B ===
def worked_b():
    result = policy_metrics([0.99, 0.97, 0.3, 0.2], [0, 0, 1, 1], 0.85)
    assert result["coverage"] == 0.5 and result["accuracy"] == 0 and np.isclose(result["cost"], 2.7)
    assert policy_metrics([0.2, 0.3], [1, 1], 0.9)["accuracy"] is None
    print("Frozen policy on held-out outcomes:", result)


# === EXERCISES ===
def exercise_checks():
    assert policy_metrics([1, 0], [1, 0], 0)["coverage"] == 1
    assert policy_metrics([0.5], [1], 0.5)["coverage"] == 1
    assert policy_metrics([0.4], [1], 0.5)["cost"] == 0.4
    assert policy_metrics([0.6], [0], 0.5)["cost"] == 5
    for scores, y in [([], []), ([1.1], [1]), ([float("nan")], [1])]:
        try:
            policy_metrics(scores, y, 0.5)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid score accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-010: all reference checks passed")


if __name__ == "__main__":
    main()
