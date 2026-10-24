"""llm-047: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def softmax_rows(logits):
    logits = np.asarray(logits, dtype=float)
    if logits.ndim != 2 or not logits.shape[1] or not np.isfinite(logits).all():
        raise ValueError("finite router matrix required")
    mass = np.exp(logits - logits.max(1, keepdims=True))
    return mass / mass.sum(1, keepdims=True)


def mixture(x, logits, experts, k):
    x, logits, experts = (np.asarray(value, dtype=float) for value in (x, logits, experts))
    if (
        x.ndim != 2
        or logits.ndim != 2
        or experts.ndim != 3
        or len(x) != len(logits)
        or logits.shape[1] != len(experts)
        or x.shape[1] != experts.shape[1]
        or type(k) is not int
        or not 1 <= k <= len(experts)
    ):
        raise ValueError("expert shapes and top-k required")
    probabilities = softmax_rows(logits)
    indices = np.argsort(-logits, axis=1, kind="stable")[:, :k]
    selected = np.take_along_axis(probabilities, indices, axis=1)
    gates = selected / selected.sum(1, keepdims=True)
    output = np.zeros((len(x), experts.shape[2]))
    for row in range(len(x)):
        for slot, expert in enumerate(indices[row]):
            output[row] += gates[row, slot] * (x[row] @ experts[expert])
    return output, indices, gates


def capacity_route(x, logits, experts, capacity):
    x, logits, experts = (np.asarray(value, dtype=float) for value in (x, logits, experts))
    if (
        type(capacity) is not int
        or capacity <= 0
        or experts.shape[1:] != (x.shape[1], x.shape[1])
        or logits.shape != (len(x), len(experts))
    ):
        raise ValueError("positive capacity and square expert shapes required")
    chosen = np.argmax(logits, axis=1)
    assigned = np.bincount(chosen, minlength=len(experts))
    accepted = np.zeros(len(experts), dtype=int)
    dropped = np.zeros(len(x), dtype=bool)
    output = x.copy()
    for row, expert in enumerate(chosen):
        if accepted[expert] >= capacity:
            dropped[row] = True
            continue
        output[row] += x[row] @ experts[expert]
        accepted[expert] += 1
    return output, dropped, assigned, accepted


def verify():
    # Exercise 1: Calculate a top2 expert mixture
    x = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    experts = np.stack([np.eye(2), 2 * np.eye(2), -np.eye(2)])
    logits = np.array(
        [[np.log(3), 0.0, -100.0], [0.0, np.log(3), -100.0], [-100.0, 0.0, np.log(3)]]
    )
    output, indices, gates = mixture(x, logits, experts, 2)
    np.testing.assert_allclose(output, [[1.25, 0], [0, 1.75], [-0.25, -0.25]], atol=1e-12, rtol=0)
    np.testing.assert_allclose(gates.sum(1), 1, atol=1e-12, rtol=0)

    # Exercise 2: Enforce expert capacity with residual fallback
    tokens = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [2.0, 1.0]])
    route_logits = np.array([[5.0, 0.0], [4.0, 0.0], [0.0, 4.0], [3.0, 0.0]])
    residual, dropped, assigned, accepted = capacity_route(tokens, route_logits, experts[:2], 2)
    assert (
        assigned.tolist() == [3, 1]
        and accepted.tolist() == [2, 1]
        and dropped.tolist() == [False, False, False, True]
    )
    np.testing.assert_allclose(residual, [[2, 0], [0, 2], [3, 3], [2, 1]], atol=1e-12, rtol=0)

    # Exercise 3: Compute a load-balancing term
    fractions = np.array([0.75, 0.25])
    mean_probability = np.array([0.7, 0.3])
    coefficient = 0.01
    loss = coefficient * 2 * np.dot(fractions, mean_probability)
    np.testing.assert_allclose(loss, 0.012, atol=1e-12, rtol=0)
    np.testing.assert_allclose(
        coefficient * 2 * np.dot([0.5, 0.5], [0.5, 0.5]), 0.01, atol=1e-12, rtol=0
    )

    # Exercise 4: Trace a local router gradient
    h = 1e-6
    plus = logits.copy()
    minus = logits.copy()
    plus[0, 0] += h
    minus[0, 0] -= h
    numeric = (mixture(x, plus, experts, 2)[0][0, 0] - mixture(x, minus, experts, 2)[0][0, 0]) / (
        2 * h
    )
    np.testing.assert_allclose(numeric, -3 / 16, atol=1e-8, rtol=0)

    # Exercise 5: Separate total andactive parameter counts
    expert_count, width, hidden, active = 8, 64, 128, 2
    assert expert_count * 2 * width * hidden == 131072
    assert active * 2 * width * hidden == 32768

    # Exercise 6: Validate routing policy andties
    _, tied, _ = mixture(np.ones((1, 2)), np.zeros((1, 3)), experts, 2)
    assert tied.tolist() == [[0, 1]]
    for action in [
        lambda: mixture(x, logits, experts, 0),
        lambda: capacity_route(tokens, route_logits, experts[:2], 0),
    ]:
        try:
            action()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid routing policy accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
