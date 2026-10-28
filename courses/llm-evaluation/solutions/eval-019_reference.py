import numpy as np


def probability_vector(values):
    x = np.asarray(values, float)
    if (
        x.ndim != 1
        or not x.size
        or not np.isfinite(x).all()
        or np.any(x <= 0)
        or not np.isclose(x.sum(), 1)
    ):
        raise ValueError("Strictly positive normalized probabilities required")
    return x


def softmax(logits):
    x = np.asarray(logits, float)
    weights = np.exp(x - x.max())
    return weights / weights.sum()


def objective(p, q, reward, beta):
    p = probability_vector(p)
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if p.shape != q.shape or p.shape != r.shape or beta <= 0 or not np.isfinite(r).all():
        raise ValueError("Aligned rewards and positive beta required")
    return float(p @ r - beta * np.sum(p * np.log(p / q)))


def optimal_policy(q, reward, beta):
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if r.shape != q.shape or beta <= 0 or not np.isfinite(r).all() or not np.isfinite(beta):
        raise ValueError("Invalid policy objective")
    return softmax(np.log(q) + r / beta)


def logit_gradient(logits, q, reward, beta):
    p = softmax(logits)
    direction = np.asarray(reward) - beta * (np.log(p / np.asarray(q)) + 1)
    return p * (direction - p @ direction)


# === EXAMPLE A ===
def worked_a():
    q = np.array([0.5, 0.5])
    r = np.array([1.0, 0.0])
    p = optimal_policy(q, r, 1.0)
    assert np.isclose(p[0], np.e / (1 + np.e))
    assert objective(p, q, r, 1) > objective(q, q, r, 1)
    logits = np.array([0.2, -0.1])
    h = 1e-5
    numeric = np.array(
        [
            (
                objective(softmax(logits + np.eye(2)[i] * h), q, r, 1)
                - objective(softmax(logits - np.eye(2)[i] * h), q, r, 1)
            )
            / (2 * h)
            for i in range(2)
        ]
    )
    np.testing.assert_allclose(logit_gradient(logits, q, r, 1), numeric, atol=1e-10)
    print("Exact policy:", p.tolist(), "regularized objective:", objective(p, q, r, 1))


# === EXAMPLE B ===
def worked_b():
    q = np.array([0.5, 0.5])
    proxy = np.array([1.0, 3.0])
    utility = np.array([1.0, -2.0])
    optimized = optimal_policy(q, proxy, 0.2)
    assert optimized @ proxy > q @ proxy and optimized @ utility < q @ utility
    assert optimized[1] > 0.999
    print(
        "Proxy improved:",
        float(optimized @ proxy),
        "independent utility:",
        float(optimized @ utility),
    )


# === EXERCISES ===
def exercise_checks():
    q = np.array([0.25, 0.75])
    r = np.array([1.0, 0.0])
    np.testing.assert_allclose(optimal_policy(q, r, 1), optimal_policy(q, r + 100, 1))
    np.testing.assert_allclose(optimal_policy(q, r, 1), optimal_policy(q, 2 * r, 2))
    assert abs(logit_gradient([0.2, 0.3], q, r, 1).sum()) < 1e-12
    assert np.isfinite(optimal_policy([0.5, 0.5], [1000, 999], 1)).all()
    try:
        optimal_policy([0, 1], [1, 0], 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported action silently smoothed")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-019: all reference checks passed")


if __name__ == "__main__":
    main()
