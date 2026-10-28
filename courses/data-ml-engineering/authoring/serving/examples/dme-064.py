"""Sampling changes a conditional distribution; stopping changes an output contract."""

import numpy as np


def distribution(logits, temperature, top_k):
    values = np.asarray(logits, dtype=float)
    if temperature <= 0 or not 1 <= top_k <= len(values):
        raise ValueError("positive temperature and bounded k required")
    retained = np.argsort(-values, kind="stable")[:top_k]
    scores = values[retained] / temperature
    probabilities = np.exp(scores - scores.max())
    probabilities /= probabilities.sum()
    result = np.zeros_like(values)
    result[retained] = probabilities
    return result


def example_one():
    p = distribution([0.0, np.log(2), np.log(3)], 1.0, 3)
    np.testing.assert_allclose(p, [1 / 6, 2 / 6, 3 / 6])
    truncated = distribution([0.0, np.log(2), np.log(3)], 1.0, 2)
    np.testing.assert_allclose(truncated, [0.0, 0.4, 0.6])
    cold = distribution([0.0, np.log(2), np.log(3)], 0.5, 3)
    np.testing.assert_allclose(cold, [1 / 14, 4 / 14, 9 / 14])
    print("full", p, "top-2", truncated, "colder", cold)
    a = np.random.default_rng(17).choice(3, size=12, p=p)
    b = np.random.default_rng(17).choice(3, size=12, p=p)
    np.testing.assert_array_equal(a, b)


def example_two():
    stop = "<END>"
    chunks = ["answer <E", "ND> hidden"]
    pending = ""
    visible = ""
    for chunk in chunks:
        pending += chunk
        found = pending.find(stop)
        if found >= 0:
            visible += pending[:found]
            break
        hold = max([0] + [size for size in range(1, len(stop)) if pending.endswith(stop[:size])])
        visible += pending[:-hold] if hold else pending
        pending = pending[-hold:] if hold else ""
    assert visible == "answer "
    print("Stop string omitted across token/event boundaries:", repr(visible))
    print("EOS identity, string match and output-token budget are separate finish reasons.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
