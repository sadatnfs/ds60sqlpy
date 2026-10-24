import numpy as np
from scipy import stats
from itertools import combinations


def paired_and_welch():
    before = np.array([10.0, 30.0, 50.0, 70.0, 90.0, 110.0])
    changes = np.array([1.0, 2.0, 1.0, 2.0, 1.0, 2.0])
    after = before + changes
    paired = stats.ttest_rel(after, before)
    independent = stats.ttest_ind(after, before, equal_var=False)
    assert paired.pvalue < 0.01 and independent.pvalue > 0.8
    print("Paired p:", paired.pvalue, "unpaired p:", independent.pvalue)


def exact_randomization():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    observed = y[2:].mean() - y[:2].mean()
    contrasts = []
    for treated in combinations(range(4), 2):
        mask = np.zeros(4, dtype=bool)
        mask[list(treated)] = True
        contrasts.append(y[mask].mean() - y[~mask].mean())
    p = np.mean(np.abs(contrasts) >= abs(observed))
    assert np.isclose(p, 1 / 3)
    print("Six valid assignments, exact two-sided p:", p)


def equivalence():
    delta, se, margin = 0.1, 0.1, 0.5
    lower, upper = delta + np.array([-1, 1]) * stats.norm.ppf(0.95) * se
    assert lower > -margin and upper < margin
    print("90% equivalence interval:", lower, upper, "inside +/-", margin)


def main():
    paired_and_welch()
    exact_randomization()
    equivalence()


if __name__ == "__main__":
    main()
