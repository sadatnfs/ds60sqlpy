import numpy as np


def attention(q, k, v, allowed):
    q, k, v = (np.asarray(value, dtype=np.float64) for value in (q, k, v))
    allowed = np.asarray(allowed)
    if any(value.ndim != 2 for value in (q, k, v)):
        raise ValueError("q, k and v must be matrices")
    count, width = q.shape
    if count == 0 or width == 0 or v.shape[1] == 0:
        raise ValueError("nonempty token and feature axes required")
    if k.shape != (count, width) or v.shape[0] != count:
        raise ValueError("self-attention shapes do not agree")
    if allowed.dtype != np.bool_:
        raise TypeError("allowed must be boolean")
    if allowed.shape != (count, count):
        raise ValueError("allowed must have shape (tokens, tokens)")
    if not allowed.any(axis=1).all():
        raise ValueError("each query needs at least one key")
    if not all(np.isfinite(value).all() for value in (q, k, v)):
        raise ValueError("finite inputs required")
    scores = (q @ k.T) / np.sqrt(width)
    if not np.isfinite(scores[allowed]).all():
        raise ValueError("finite allowed scores required")
    masked = np.where(allowed, scores, -np.inf)
    shifted = masked - masked.max(axis=1, keepdims=True)
    weights = np.exp(shifted)
    weights /= weights.sum(axis=1, keepdims=True)
    return weights @ v, weights


def verify():
    q = np.zeros((3, 2), dtype=np.float64)
    k = q.copy()
    v = np.array([[2.0, 0.0], [0.0, 2.0], [6.0, 6.0]])
    allowed = np.tri(3, dtype=bool)
    output, weights = attention(q, k, v, allowed)
    expected = np.array([[2.0, 0.0], [1.0, 1.0], [8 / 3, 8 / 3]])
    np.testing.assert_allclose(output, expected, rtol=0, atol=1e-12)
    np.testing.assert_allclose(weights.sum(axis=1), 1.0, rtol=0, atol=1e-12)
    for cut in range(1, 4):
        prefix, _ = attention(q[:cut], k[:cut], v[:cut], np.tri(cut, dtype=bool))
        np.testing.assert_allclose(output[:cut], prefix, rtol=0, atol=1e-12)
    print(output)

    # Exercise 1: exact reference checks
    expected_weights = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.5, 0.5, 0.0],
            [1 / 3, 1 / 3, 1 / 3],
        ]
    )
    expected_output = np.array([[2.0, 0.0], [1.0, 1.0], [8 / 3, 8 / 3]])
    np.testing.assert_allclose(weights, expected_weights, rtol=0, atol=1e-12)
    np.testing.assert_allclose(output, expected_output, rtol=0, atol=1e-12)
    np.testing.assert_allclose(weights.sum(axis=1), [1.0, 1.0, 1.0], rtol=0, atol=1e-12)
    print("exercise 1: mixtures and row masses agree")

    # Exercise 2: exact reference checks
    original_v = v.copy()
    future_v = v.copy()
    future_v[2] = [100.0, 200.0]
    causal, _ = attention(q, k, future_v, np.tri(3, dtype=bool))
    unmasked, _ = attention(q, k, future_v, np.ones((3, 3), dtype=bool))
    np.testing.assert_allclose(causal[:2], expected_output[:2], rtol=0, atol=1e-12)
    np.testing.assert_allclose(causal[2], [34.0, 202 / 3], rtol=0, atol=1e-12)
    np.testing.assert_allclose(unmasked, np.tile([34.0, 202 / 3], (3, 1)), rtol=0, atol=1e-12)
    np.testing.assert_array_equal(v, original_v)
    assert not np.allclose(unmasked[:2], expected_output[:2])
    print("exercise 2: causal prefix unchanged; unmasked prefix changed")

    # Exercise 3: exact reference checks
    def check_prefixes(query, key, value):
        count = len(query)
        full, _ = attention(query, key, value, np.tri(count, dtype=bool))
        for cut in range(1, count + 1):
            prefix, _ = attention(query[:cut], key[:cut], value[:cut], np.tri(cut, dtype=bool))
            np.testing.assert_allclose(full[:cut], prefix, rtol=0, atol=1e-12)
        return full

    nonuniform_q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, 1.0]])
    nonuniform_k = nonuniform_q.copy()
    nonuniform_v = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]])
    full = check_prefixes(nonuniform_q, nonuniform_k, nonuniform_v)
    future_q, future_k, future_values = (
        value.copy() for value in (nonuniform_q, nonuniform_k, nonuniform_v)
    )
    future_q[2:] += 3.0
    future_k[2:] *= -4.0
    future_values[2:] += 100.0
    changed = check_prefixes(future_q, future_k, future_values)
    np.testing.assert_allclose(changed[:2], full[:2], rtol=0, atol=1e-12)
    assert not np.allclose(changed[2:], full[2:])
    print("exercise 3: all four cuts and future perturbations passed")

    # Exercise 4: exact reference checks
    broken_weights = np.full((3, 3), 1 / 3) * np.tri(3, dtype=bool)
    broken_output = broken_weights @ v
    np.testing.assert_allclose(broken_weights.sum(axis=1), [1 / 3, 2 / 3, 1.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        broken_output, [[2 / 3, 0.0], [2 / 3, 2 / 3], [8 / 3, 8 / 3]], rtol=0, atol=1e-12
    )
    repaired, repaired_weights = attention(q, k, v, np.tri(3, dtype=bool))
    np.testing.assert_allclose(repaired, expected_output, rtol=0, atol=1e-12)
    np.testing.assert_allclose(repaired_weights.sum(axis=1), 1.0, rtol=0, atol=1e-12)
    print("exercise 4: masked-before-normalization repair passed")

    # Exercise 5: exact reference checks
    def expect_failure(error_type, operation, message=None):
        try:
            operation()
        except error_type as error:
            if message is not None:
                assert message in str(error)
        else:
            raise AssertionError("invalid input was accepted")

    empty = np.empty((0, 2))
    expect_failure(ValueError, lambda: attention(empty, empty, empty, np.empty((0, 0), dtype=bool)))
    expect_failure(TypeError, lambda: attention(q, k, v, np.tri(3, dtype=int)))
    expect_failure(ValueError, lambda: attention(q, k, v, np.ones((3, 2), dtype=bool)))
    no_key = np.tri(3, dtype=bool)
    no_key[1] = False
    expect_failure(
        ValueError, lambda: attention(q, k, v, no_key), "each query needs at least one key"
    )
    nonfinite = v.copy()
    nonfinite[0, 0] = np.nan
    expect_failure(
        ValueError, lambda: attention(q, k, nonfinite, allowed), "finite inputs required"
    )
    valid_again, _ = attention(q, k, v, allowed)
    assert np.isfinite(valid_again).all()
    np.testing.assert_allclose(valid_again, expected_output, rtol=0, atol=1e-12)
    print("exercise 5: five rejected cases; valid fixture still works")

    # Exercise 6: exact reference checks
    ids = np.array([2, 5, 7, 3], dtype=np.int64)
    inputs, labels = ids[:-1], ids[1:]
    np.testing.assert_array_equal(inputs, [2, 5, 7])
    np.testing.assert_array_equal(labels, [5, 7, 3])
    pairs = list(zip(inputs.tolist(), labels.tolist(), strict=True))
    assert pairs == [(2, 5), (5, 7), (7, 3)]
    assert labels.size == 3
    label_mask = np.tri(len(inputs), dtype=bool)
    assert label_mask[0, 0]
    assert not label_mask[0, 1]
    np.testing.assert_array_equal(label_mask[0], [True, False, False])

    # Two different filenames still belong to the same source-document family.
    family = {"doc-a": "A", "doc-a-copy": "A"}
    training_ids, validation_ids = ["doc-a"], ["doc-a-copy"]
    training_families = {family[name] for name in training_ids}
    validation_families = {family[name] for name in validation_ids}
    assert training_families & validation_families == {"A"}
    print("exercise 6:", pairs, "duplicate-family leakage detected")

    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
