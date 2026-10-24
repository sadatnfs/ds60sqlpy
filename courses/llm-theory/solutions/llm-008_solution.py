from __future__ import annotations

import numpy as np


def lookup(table, ids):
    table = np.asarray(table, dtype=np.float64)
    ids = np.asarray(ids)
    if table.ndim != 2 or not all(table.shape) or not np.isfinite(table).all():
        raise ValueError("finite nonempty embedding table required")
    if ids.ndim != 1:
        raise ValueError("token IDs must be a vector")
    if ids.size == 0:
        return np.empty((0, table.shape[1]), dtype=np.float64)
    if not np.issubdtype(ids.dtype, np.integer) or ids.dtype == np.bool_:
        raise TypeError("integer token IDs required")
    if (ids < 0).any() or (ids >= len(table)).any():
        raise ValueError("token ID outside vocabulary")
    return table[ids].copy()


def verify():
    table = np.array([[1, 0], [0, 1], [2, 2], [-1, 1]], dtype=np.float64)
    ids = np.array([2, 0, 2])
    # Exercise 1: selected feature axis
    expected = np.array([[2, 2], [1, 0], [2, 2]])
    np.testing.assert_array_equal(lookup(table, ids), expected)
    # Exercise 2: one-hot equivalence
    np.testing.assert_array_equal(np.eye(4)[ids] @ table, expected)
    # Exercise 3: illegal token IDs
    for error, values in ((ValueError, [-1]), (ValueError, [4]), (TypeError, [1.5])):
        try:
            lookup(table, values)
        except error:
            pass
        else:
            raise AssertionError("invalid token ID accepted")
    # Exercise 4: a declared empty lookup shape
    assert lookup(table, []).shape == (0, 2)
    # Exercise 5: output storage ownership
    original = table.copy()
    output = lookup(table, ids)
    output[0, 0] = 999
    np.testing.assert_array_equal(table, original)
    np.testing.assert_array_equal(output[2], [2, 2])
    # Exercise 6: vocabulary order and ID order must move together
    np.testing.assert_array_equal(lookup(table[[2, 0, 3, 1]], [0, 1, 0]), expected)
    return {"shape": [3, 2], "vocabulary": 4, "features": 2}


if __name__ == "__main__":
    print(verify())
