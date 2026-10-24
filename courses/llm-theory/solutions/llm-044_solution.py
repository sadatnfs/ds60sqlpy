"""llm-044: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def rotate(vector, angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s], [s, c]]) @ np.asarray(vector, dtype=float)


def rope(values, positions, base=10000.0):
    values = np.asarray(values, dtype=np.float64)
    positions = np.asarray(positions, dtype=np.float64)
    if (
        values.ndim != 2
        or values.shape[1] == 0
        or values.shape[1] % 2
        or positions.shape != (len(values),)
    ):
        raise ValueError("even feature width and one position per row required")
    if (
        not np.isfinite(values).all()
        or not np.isfinite(positions).all()
        or not np.isfinite(base)
        or base <= 0
    ):
        raise ValueError("finite rotary inputs required")
    width = values.shape[1]
    pairs = values.reshape(len(values), width // 2, 2)
    angles = positions[:, None] * base ** (-2 * np.arange(width // 2) / width)
    c, s = np.cos(angles), np.sin(angles)
    result = np.empty_like(pairs)
    result[..., 0] = pairs[..., 0] * c - pairs[..., 1] * s
    result[..., 1] = pairs[..., 0] * s + pairs[..., 1] * c
    return result.reshape(values.shape)


def verify():
    # Exercise 1: Rotate a two-dimensional vector
    vector = np.array([1.0, 0.0])
    rotated = rotate(vector, np.pi / 2)
    np.testing.assert_allclose(rotated, [0, 1], atol=1e-12, rtol=0)
    np.testing.assert_allclose(np.linalg.norm(rotated), 1, atol=1e-12, rtol=0)

    # Exercise 2: Verify the relative dot-product identity
    q = np.array([1.0, 2.0])
    k = np.array([3.0, -1.0])
    m = 0.3
    n = 1.1
    left = rotate(q, m) @ rotate(k, n)
    right = q @ rotate(k, n - m)
    np.testing.assert_allclose(left, right, atol=1e-12, rtol=0)

    # Exercise 3: Inspect an ALiBi causal row
    positions = np.arange(3)
    score = -np.log(2) * (2 - positions)
    mass = np.exp(score - score.max())
    weights = mass / mass.sum()
    np.testing.assert_allclose(weights, [1 / 7, 2 / 7, 4 / 7], atol=1e-12, rtol=0)

    # Exercise 4: Apply multi-frequency RoPE
    values = np.array([[1.0, 0.0, 3.0, 4.0], [2.0, 1.0, 0.0, 2.0]])
    encoded = rope(values, np.array([0, 1]), base=10000.0)
    np.testing.assert_allclose(
        np.linalg.norm(encoded.reshape(2, 2, 2), axis=-1),
        np.linalg.norm(values.reshape(2, 2, 2), axis=-1),
        atol=1e-12,
        rtol=0,
    )
    np.testing.assert_allclose(10000.0 ** (-2 * np.arange(2) / 4), [1, 0.01], atol=1e-12, rtol=0)

    # Exercise 5: Catch a cache offset reset
    keys = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    full = rope(keys, np.arange(3))
    incremental = rope(keys[2:], np.array([2]))
    reset = rope(keys[2:], np.array([0]))
    np.testing.assert_allclose(incremental, full[2:], atol=1e-12, rtol=0)
    assert not np.allclose(reset, full[2:])

    # Exercise 6: Separate computability from extrapolation evidence
    far = rope(np.array([[1.0, 0.0, 1.0, 0.0]]), np.array([1_000_000]))
    assert np.isfinite(far).all()
    report = {"formula_evaluated": True, "long_context_quality_verified": False}
    assert not report["long_context_quality_verified"]
    try:
        rope(np.ones((1, 3)), np.array([0]))
    except ValueError:
        pass
    else:
        raise AssertionError("odd rotary width accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
