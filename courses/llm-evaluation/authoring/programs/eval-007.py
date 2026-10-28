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


# === EXAMPLE A ===
def worked_a():
    unadjusted = 1 - (1 - 0.05) ** 3
    adjusted = 1 - (1 - 0.05 / 3) ** 3
    assert np.isclose(unadjusted, 0.142625) and adjusted < 0.05
    assert bonferroni([0.01, 0.03, 0.2]).tolist() == [True, False, False]
    print("Independent three-test family error:", unadjusted, "adjusted:", adjusted)


# === EXAMPLE B ===
def worked_b():
    flags = spent_decisions([0.02, 0.02, 0.02], [0.01, 0.015, 0.025])
    assert flags.tolist() == [False, False, True]
    print("Declared-look crossings:", flags.tolist())


# === EXERCISES ===
def exercise_checks():
    assert bonferroni([0.05]).tolist() == [True]
    assert bonferroni([0.02, 0.02, 0.02]).tolist() == [False] * 3
    assert not spent_decisions([0.01], [0]).item()
    for p, a in [([0.1], [0.06]), ([0.1, 0.2], [0.01]), ([float("nan")], [0.01])]:
        try:
            spent_decisions(p, a)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid monitoring plan accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-007: all reference checks passed")


if __name__ == "__main__":
    main()
