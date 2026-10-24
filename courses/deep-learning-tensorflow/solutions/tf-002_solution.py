from __future__ import annotations

import numpy as np


def paired_difference(left, right):
    left, right = (np.asarray(value, dtype=np.float64) for value in (left, right))
    if left.ndim != 1 or right.ndim != 1 or left.shape != right.shape:
        raise ValueError("equal vector shapes required")
    if left.size == 0:
        raise ValueError("nonempty vectors required")
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ValueError("finite vectors required")
    return left - right


def verify():
    # Exercise 1: trace two different layouts
    x = np.array([1, 2, 3])
    y = np.array([2, 4, 6])
    np.testing.assert_array_equal(x - y, [-1, -2, -3])
    np.testing.assert_array_equal(x - y.reshape(3, 1), [[-1, 0, 1], [-3, -2, -1], [-5, -4, -3]])
    # Exercise 2: reject a column pairing
    result = paired_difference(x, y)
    assert result.dtype == np.float64
    try:
        paired_difference(x, y.reshape(3, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("column pairing accepted")
    # Exercise 3: integer versus fractional storage
    original = x.copy()
    try:
        x -= 0.5
    except TypeError:
        pass
    else:
        raise AssertionError("integer update unexpectedly accepted")
    floating = original.astype(np.float64)
    floating -= 0.5
    np.testing.assert_array_equal(floating, [0.5, 1.5, 2.5])
    np.testing.assert_array_equal(x, original)
    # Exercise 4: empty and nonfinite inputs
    for a, b in (([], []), ([1, np.nan], [2, 3])):
        try:
            paired_difference(a, b)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid vector accepted")
    assert np.isfinite(paired_difference(x, y)).all()
    # Exercise 5: numeric tolerance
    assert np.isclose(np.float64(0.1) + np.float64(0.2), 0.3, rtol=0, atol=1e-12)
    # Exercise 6: explicit unit conversion
    np.testing.assert_array_equal(paired_difference(np.array([100, 200]) / 100, [1, 2]), [0, 0])
    return {"shape": list(result.shape), "dtype": str(result.dtype)}


if __name__ == "__main__":
    print(verify())
