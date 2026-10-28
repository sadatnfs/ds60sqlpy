import numpy as np


def group_advantages(rewards):
    r = np.asarray(rewards, float)
    if r.ndim != 1 or len(r) < 2 or not np.isfinite(r).all():
        raise ValueError("At least two finite group rewards required")
    centered = r - r.mean()
    scale = float(np.sqrt(np.mean(centered**2)))
    return np.zeros_like(r) if scale == 0 else centered / scale


def kl_terms(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    if (
        p.shape != q.shape
        or p.ndim != 1
        or not np.isfinite(p).all()
        or not np.isfinite(q).all()
        or np.any(p <= 0)
        or np.any(q <= 0)
        or not np.isclose(p.sum(), 1)
        or not np.isclose(q.sum(), 1)
    ):
        raise ValueError("Positive normalized distributions required")
    ratio = q / p
    return ratio - np.log(ratio) - 1


def worked_a():
    a = group_advantages([0, 1, 2, 3])
    assert np.isclose(a.mean(), 0) and np.isclose(np.mean(a * a), 1)
    np.testing.assert_allclose(a, group_advantages([10, 11, 12, 13]))
    np.testing.assert_allclose(a, group_advantages([0, 2, 4, 6]))
    assert group_advantages([0, 0, 0]).tolist() == [0.0, 0.0, 0.0]
    print("Group advantages:", a.tolist(), "constant group:", group_advantages([1, 1]).tolist())


worked_a()

# Task 1: Add a common constant to 0,1,2,3.
# Task 2: Compare all-zero and all-one reward groups.
# Task 3: Give advantages-1,+1 to responses of length 2,4.
# Task 4: Average case B KL terms under the old uniform policy.
# Task 5: Evaluate the centered two-action surrogate at zero log odds.
# Task 6: Change standard-deviation correction, epsilon or token reduction.

# Implement your six changes below.
