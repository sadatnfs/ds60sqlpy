import numpy as np


def policies(behavior, target):
    b = np.asarray(behavior, float)
    p = np.asarray(target, float)
    if (
        b.shape != p.shape
        or b.ndim != 2
        or np.any(b < 0)
        or np.any(p < 0)
        or not np.isfinite(b).all()
        or not np.isfinite(p).all()
        or not np.allclose(b.sum(1), 1)
        or not np.allclose(p.sum(1), 1)
    ):
        raise ValueError("Normalized finite contextual policies required")
    if np.any((p > 0) & (b == 0)):
        raise ValueError("Target has unsupported actions")
    return b, p


def estimate(log, behavior, target, outcome_model):
    b, p = policies(behavior, target)
    q = np.asarray(outcome_model, float)
    if q.shape != b.shape or not np.isfinite(q).all() or not log:
        raise ValueError("Outcome model and nonempty log required")
    weights = []
    weighted = []
    dr = []
    for context, action, reward in log:
        if (
            type(context) is not int
            or type(action) is not int
            or not 0 <= context < b.shape[0]
            or not 0 <= action < b.shape[1]
            or not np.isfinite(reward)
        ):
            raise ValueError("Malformed logged event")
        if b[context, action] <= 0:
            raise ValueError("Impossible logged action")
        weight = p[context, action] / b[context, action]
        weights.append(weight)
        weighted.append(weight * reward)
        dr.append(p[context] @ q[context] + weight * (reward - q[context, action]))
    w = np.asarray(weights)
    if w.sum() <= 0:
        raise ValueError("No observed target weight")
    return {
        "ips": float(np.mean(weighted)),
        "snis": float(np.sum(weighted) / w.sum()),
        "dr": float(np.mean(dr)),
        "weight_ess": float(w.sum() ** 2 / np.sum(w * w)),
    }


def fixture(counts):
    reward = np.array([[1.0, 0.0], [0.0, 1.0]])
    return [
        (s, a, float(reward[s, a])) for s in range(2) for a in range(2) for _ in range(counts[s][a])
    ]


def worked_a():
    behavior = [[0.8, 0.2], [0.3, 0.7]]
    target = [[0.5, 0.5], [0.8, 0.2]]
    reward = [[1.0, 0.0], [0.0, 1.0]]
    result = estimate(fixture([[16, 4], [6, 14]]), behavior, target, reward)
    assert (
        np.isclose(result["ips"], 0.35)
        and np.isclose(result["snis"], 0.35)
        and np.isclose(result["dr"], 0.35)
    )
    print("Constructed balanced log:", result)


worked_a()

# Task 1: Set the target policy equal to the behavior policy in case A.
# Task 2: Use target rows[0.9,0.1] and[0.1,0.9] with the exact synthetic outcome table.
# Task 3: Give an action zero behavior probability but positive target probability.
# Task 4: Set every outcome-model prediction to zero.
# Task 5: Compare IPS and SNIS in case B.
# Task 6: Choose a policy after inspecting many estimates from the same log.

# Implement your six changes below.
