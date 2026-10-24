from __future__ import annotations

import numpy as np


def softmax(scores, allowed=None):
    scores = np.asarray(scores, dtype=np.float64)
    if scores.ndim != 1 or scores.size == 0 or not np.isfinite(scores).all():
        raise ValueError("finite nonempty score vector required")
    if allowed is None:
        allowed = np.ones(scores.shape, dtype=bool)
    allowed = np.asarray(allowed)
    if allowed.dtype != np.bool_:
        raise TypeError("allowed must be boolean")
    if allowed.shape != scores.shape or not allowed.any():
        raise ValueError("same-shaped mask with at least one allowed choice required")
    masked = np.where(allowed, scores, -np.inf)
    mass = np.exp(masked - masked.max())
    return mass / mass.sum()


def verify():
    # Exercise 1: shared offsets
    for values in ([0, 0], [1000, 1000]):
        np.testing.assert_allclose(softmax(values), [0.5, 0.5], rtol=0, atol=1e-12)
    # Exercise 2: unequal stable scores
    values = np.array([0, np.log(3)])
    np.testing.assert_allclose(softmax(values), [0.25, 0.75], rtol=0, atol=1e-12)
    np.testing.assert_allclose(softmax(values + 1000), [0.25, 0.75], rtol=0, atol=1e-12)
    # Exercise 3: forbidden high score
    np.testing.assert_allclose(
        softmax([0, 100, 0], [True, False, True]), [0.5, 0, 0.5], rtol=0, atol=1e-12
    )
    # Exercise 4: reduction axis
    global_weights = np.ones((2, 2)) / 4
    np.testing.assert_array_equal(global_weights.sum(axis=1), [0.5, 0.5])
    np.testing.assert_array_equal(np.vstack([softmax([0, 0])] * 2).sum(axis=1), [1, 1])
    # Exercise 5: invalid categorical rows
    cases = [
        (ValueError, [], None),
        (ValueError, [np.nan], None),
        (TypeError, [0, 0], [1, 1]),
        (ValueError, [0, 0], [False, False]),
    ]
    for error_type, scores, mask in cases:
        try:
            softmax(scores, mask)
        except error_type:
            pass
        else:
            raise AssertionError("invalid distribution accepted")
    # Exercise 6: temperature without certainty
    expected = np.array([1, np.sqrt(3)]) / (1 + np.sqrt(3))
    np.testing.assert_allclose(softmax(values / 2), expected, rtol=0, atol=1e-12)
    assert softmax(values / 2).argmax() == 1
    return {"probabilities": softmax(values).tolist(), "row_sum": float(softmax(values).sum())}


if __name__ == "__main__":
    print(verify())
