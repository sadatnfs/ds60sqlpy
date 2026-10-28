import numpy as np


def gae(rewards, values, terminals, gamma=0.9, lam=0.8):
    r = np.asarray(rewards, float)
    v = np.asarray(values, float)
    d = np.asarray(terminals)
    if (
        d.dtype.kind != "b"
        or r.ndim != 1
        or v.shape != (len(r) + 1,)
        or d.shape != r.shape
        or not 0 <= gamma <= 1
        or not 0 <= lam <= 1
    ):
        raise ValueError("One aligned rollout required")
    if not np.isfinite(r).all() or not np.isfinite(v).all():
        raise ValueError("Finite rewards and values required")
    result = np.zeros_like(r)
    carry = 0.0
    for t in reversed(range(len(r))):
        residual = r[t] + gamma * (not d[t]) * v[t + 1] - v[t]
        carry = residual + gamma * lam * (not d[t]) * carry
        result[t] = carry
    return result


def clipped_terms(ratio, advantage, epsilon=0.2):
    ratio = np.asarray(ratio, float)
    advantage = np.asarray(advantage, float)
    if (
        ratio.shape != advantage.shape
        or np.any(ratio < 0)
        or not np.isfinite(ratio).all()
        or not np.isfinite(advantage).all()
        or not 0 < epsilon < 1
    ):
        raise ValueError("Invalid PPO arrays")
    return np.minimum(ratio * advantage, np.clip(ratio, 1 - epsilon, 1 + epsilon) * advantage)


def kl(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    return float(np.sum(p * np.log(p / q)))


# === EXAMPLE A ===
def worked_a():
    terminal = gae([1, 2], [0.5, 0.4, 0.2], [False, True])
    truncated = gae([1, 2], [0.5, 0.4, 0.2], [False, False])
    np.testing.assert_allclose(terminal, [2.012, 1.6])
    np.testing.assert_allclose(truncated, [2.1416, 1.78])
    print("Terminal advantages:", terminal.tolist(), "truncated:", truncated.tolist())


# === EXAMPLE B ===
def worked_b():
    result = clipped_terms([1.5, 0.5, 0.5, 1.5], [1, 1, -1, -1])
    np.testing.assert_allclose(result, [1.2, 0.5, -0.8, -1.5])
    old = np.array([0.5, 0.49, 0.01])
    p = np.array([0.6, 0.39, 0.01])
    other = np.array([0.6, 0.01, 0.39])
    assert np.isclose(
        clipped_terms([p[0] / old[0]], [1])[0], clipped_terms([other[0] / old[0]], [1])[0]
    )
    assert kl(other, old) > kl(p, old)
    print("Clipped terms:", result.tolist(), "different full KL:", kl(p, old), kl(other, old))


# === EXERCISES ===
def exercise_checks():
    np.testing.assert_allclose(gae([1, 2], [0.5, 0.4, 0.2], [False, True], lam=0), [0.86, 1.6])
    np.testing.assert_allclose(gae([1, 2], [0.5, 0.4, 0.2], [True, True]), [0.5, 1.6])
    np.testing.assert_allclose(clipped_terms([1, 1], [2, -2]), [2, -2])
    assert clipped_terms([100], [0])[0] == 0
    for ratio, advantage in [([1], [1, 2]), ([-1], [1])]:
        try:
            clipped_terms(ratio, advantage)
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed ratio accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-021: all reference checks passed")


if __name__ == "__main__":
    main()
