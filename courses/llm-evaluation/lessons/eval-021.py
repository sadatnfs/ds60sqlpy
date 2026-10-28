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


def worked_a():
    terminal = gae([1, 2], [0.5, 0.4, 0.2], [False, True])
    truncated = gae([1, 2], [0.5, 0.4, 0.2], [False, False])
    np.testing.assert_allclose(terminal, [2.012, 1.6])
    np.testing.assert_allclose(truncated, [2.1416, 1.78])
    print("Terminal advantages:", terminal.tolist(), "truncated:", truncated.tolist())


worked_a()

# Task 1: Set lambda 0 in case A.
# Task 2: Mark both steps terminal in the arithmetic helper.
# Task 3: Use ratio 1.5 and advantage 1 with epsilon 0.2.
# Task 4: Use ratio 1.5 and advantage-1.
# Task 5: Compare the two policies in case B.
# Task 6: Explain which tensors should be detached during policy optimization.

# Implement your six changes below.
