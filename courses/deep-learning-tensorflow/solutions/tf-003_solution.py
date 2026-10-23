from __future__ import annotations

import numpy as np


def affine(x, weight, bias):
    x, weight, bias = (np.asarray(v, dtype=np.float64) for v in (x, weight, bias))
    if x.ndim != 2 or weight.ndim != 2 or not all(x.shape) or not all(weight.shape):
        raise ValueError("nonempty feature and weight matrices required")
    if x.shape[1] != weight.shape[0]:
        raise ValueError("input-feature dimensions do not match")
    if bias.ndim > 1 or (bias.ndim == 1 and bias.shape != (weight.shape[1],)):
        raise ValueError("bias must be scalar or output-length vector")
    if not all(np.isfinite(v).all() for v in (x, weight, bias)):
        raise ValueError("finite affine inputs required")
    return x @ weight + bias


def verify():
    x = np.array([[1, 2, 3], [0, 1, 0]])
    w = np.array([[1], [0], [-1]])
    # Exercise 1: explicit scalar terms
    np.testing.assert_array_equal(affine(x, w, 2), [[0], [2]])
    # Exercise 2: independent batch extension
    np.testing.assert_array_equal(affine(np.vstack([x, [3, 0, 0]]), w, 2), [[0], [2], [5]])
    # Exercise 3: feature mismatch
    try:
        affine(x, np.ones((2, 1)), 2)
    except ValueError:
        pass
    else:
        raise AssertionError("feature mismatch accepted")
    # Exercise 4: output bias contract
    np.testing.assert_array_equal(affine(x, w, [2]), affine(x, w, 2))
    try:
        affine(x, w, [2, 3, 4])
    except ValueError:
        pass
    else:
        raise AssertionError("feature-length bias accepted")
    # Exercise 5: two outputs
    np.testing.assert_array_equal(affine(x, [[1, 0], [0, 1], [-1, 1]], [2, -1]), [[0, 4], [2, 0]])
    # Exercise 6: paired unit/weight conversion
    np.testing.assert_allclose(
        affine([[100], [200]], [[0.02]], 1), affine([[1], [2]], [[2]], 1), rtol=0, atol=1e-12
    )
    return {"output": affine(x, w, 2).tolist(), "shape": [2, 1]}


if __name__ == "__main__":
    print(verify())
