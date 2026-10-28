from itertools import product

import numpy as np


def sign_test(differences):
    d = np.asarray(differences, float)
    if d.ndim != 1 or not 1 <= len(d) <= 16 or not np.isfinite(d).all():
        raise ValueError("Bounded finite pairs required")
    observed = abs(d.mean())
    null = np.array([np.mean(d * np.array(signs)) for signs in product((-1, 1), repeat=len(d))])
    p = float(np.mean(np.abs(null) >= observed - 1e-12))
    return p, null


def cluster_bootstrap(means):
    x = np.asarray(means, float)
    if x.ndim != 1 or not 1 <= len(x) <= 6 or not np.isfinite(x).all():
        raise ValueError("Bounded family means required")
    return np.array(
        [np.mean(x[list(indices)]) for indices in product(range(len(x)), repeat=len(x))]
    )


# === EXAMPLE A ===
def worked_a():
    p, null = sign_test([1, 1, 1, -1])
    assert len(null) == 16 and p == 0.625
    assert sign_test([-1, -1, -1, 1])[0] == p
    print("Exact paired sign-reference tail:", p)


# === EXAMPLE B ===
def worked_b():
    distribution = cluster_bootstrap([-1, 1])
    assert distribution.tolist() == [-1.0, 0.0, 0.0, 1.0]
    np.testing.assert_allclose(np.quantile(distribution, [0.025, 0.975]), [-0.925, 0.925])
    # Observed support endpoints remain -1 and 1; interpolated percentiles differ.
    assert np.quantile(distribution, [0.025, 0.975], method="inverted_cdf").tolist() == [-1.0, 1.0]
    print("Family resample support:", distribution.tolist())


# === EXERCISES ===
def exercise_checks():
    assert sign_test([0, 0])[0] == 1
    assert sign_test([1, 1, 1, 1])[0] == 0.125
    assert np.allclose(cluster_bootstrap([0.5, 0.5]), 0.5)
    assert len(cluster_bootstrap([0, 1, 2])) == 27
    for invalid in ([], [float("nan")], [1] * 17):
        try:
            sign_test(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid sign design accepted")
    assert np.mean(cluster_bootstrap([-1, 1])) == 0


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-006: all reference checks passed")


if __name__ == "__main__":
    main()
