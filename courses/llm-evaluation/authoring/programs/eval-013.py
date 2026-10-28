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


# === EXAMPLE A ===
def worked_a():
    values = [selection_optimism(n) for n in (1, 2, 4)]
    np.testing.assert_allclose(values, [0, 0.05, 0.0875], atol=1e-12)
    print("Mean selected development noise:", values)


# === EXAMPLE B ===
def worked_b():
    dev = [[0.9, 0.8], [0.7, 0.9]]
    test = [[0.4, 0.8], [0.9, 0.5]]
    choices, selected = assess_procedure(dev, test)
    assert choices.tolist() == [0, 1]
    assert np.isclose(selected.mean(), 0.45)
    assert np.isclose(np.max(test, axis=1).mean(), 0.85)
    print("Selected by development:", choices.tolist(), "outer assessment:", selected.tolist())


# === EXERCISES ===
def exercise_checks():
    assert selection_optimism(2) > selection_optimism(1)
    choices, scores = assess_procedure([[0.5, 0.5]], [[0.1, 0.9]])
    assert choices.tolist() == [0] and scores.tolist() == [0.1]
    changed = assess_procedure([[0.9, 0.8]], [[0.0, 1.0]])[0]
    assert changed.tolist() == [0]
    for bad in (0, 13, 1.5):
        try:
            selection_optimism(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid search count accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-013: all reference checks passed")


if __name__ == "__main__":
    main()
