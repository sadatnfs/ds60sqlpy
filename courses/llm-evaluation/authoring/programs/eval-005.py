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


# === EXAMPLE A ===
def worked_a():
    means = {"routine": 0.9, "rare": 0.5}
    estimate = target_mean(means, {"routine": 0.9, "rare": 0.1})
    assert np.isclose(estimate, 0.86)
    assert np.isclose(target_mean(means, {"routine": 0.5, "rare": 0.5}), 0.7)
    print("Target estimate:", estimate, "balanced sample mean:", 0.7)


# === EXAMPLE B ===
def worked_b():
    ht, sn, ess = inclusion_estimates([1, 0], [0.5, 0.25], 10)
    assert np.isclose(ht, 0.2) and np.isclose(sn, 1 / 3) and np.isclose(ess, 1.8)
    assert inclusion_estimates([1, 0], [1, 1], 2) == (0.5, 0.5, 2.0)
    print("Known-N mean:", ht, "self-normalized mean:", sn, "weight ESS:", ess)


# === EXERCISES ===
def exercise_checks():
    assert target_mean({"a": 0.4}, {"a": 1}) == 0.4
    assert np.isclose(target_mean({"a": 0.2, "b": 0.8}, {"a": 0.25, "b": 0.75}), 0.65)
    for p in ([0, 0.5], [1.1, 0.5]):
        try:
            inclusion_estimates([1, 0], p, 2)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsupported inclusion probability accepted")
    try:
        target_mean({"a": 1}, {"a": 0.5, "b": 0.5})
    except ValueError:
        pass
    else:
        raise AssertionError("Absent target stratum accepted")
    assert inclusion_estimates([1, 0], [0.01, 1], 101)[2] < 1.03


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-005: all reference checks passed")


if __name__ == "__main__":
    main()
