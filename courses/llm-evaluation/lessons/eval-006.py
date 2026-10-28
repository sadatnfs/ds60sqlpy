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


def worked_a():
    p, null = sign_test([1, 1, 1, -1])
    assert len(null) == 16 and p == 0.625
    assert sign_test([-1, -1, -1, 1])[0] == p
    print("Exact paired sign-reference tail:", p)


worked_a()

# Task 1: Use paired differences 0,0.
# Task 2: Use differences 1,1,1,1.
# Task 3: Negate every difference in case A.
# Task 4: Compare linear interpolation with empirical inverse-CDF percentiles in case B.
# Task 5: Enumerate resamples of 0,1,2.
# Task 6: Request 17 paired differences.

# Implement your six changes below.
