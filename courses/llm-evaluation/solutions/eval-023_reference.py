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


# === EXAMPLE A ===
def worked_a():
    a = group_advantages([0, 1, 2, 3])
    assert np.isclose(a.mean(), 0) and np.isclose(np.mean(a * a), 1)
    np.testing.assert_allclose(a, group_advantages([10, 11, 12, 13]))
    np.testing.assert_allclose(a, group_advantages([0, 2, 4, 6]))
    assert group_advantages([0, 0, 0]).tolist() == [0.0, 0.0, 0.0]
    print("Group advantages:", a.tolist(), "constant group:", group_advantages([1, 1]).tolist())


# === EXAMPLE B ===
def worked_b():
    p = np.array([0.8, 0.2])
    q = np.array([0.5, 0.5])
    old = np.array([0.5, 0.5])
    terms = kl_terms(p, q)
    exact = float(np.sum(p * np.log(p / q)))
    assert np.all(terms >= 0) and np.isclose(p @ terms, exact)
    assert not np.isclose(old @ terms, exact)
    assert np.isclose(old @ ((p / old) * terms), exact)
    print("Exact current KL:", exact, "old-law average:", float(old @ terms))


# === EXERCISES ===
def exercise_checks():
    np.testing.assert_allclose(group_advantages([3, 2, 1, 0]), -group_advantages([0, 1, 2, 3]))
    response_mean = np.mean([-1.0, 1.0])
    token_mean = (-1 * 2 + 1 * 4) / 6
    assert response_mean == 0 and np.isclose(token_mean, 1 / 3)

    def surrogate(delta):
        high = 1 / (1 + np.exp(-delta))
        return 2 * high - 1

    h = 1e-5
    assert surrogate(0) == 0 and np.isclose(
        (surrogate(h) - surrogate(-h)) / (2 * h), 0.5, atol=1e-10
    )
    for r in ([1], [1, float("nan")]):
        try:
            group_advantages(r)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid reward group accepted")
    np.testing.assert_allclose(kl_terms([0.5, 0.5], [0.5, 0.5]), 0)


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-023: all reference checks passed")


if __name__ == "__main__":
    main()
