"""llm-010: bounded local reference checks. No network or persistent data writes."""

import numpy as np

def attention_parts(query, key, value, allowed=None):
    query = np.asarray(query, dtype=np.float64)
    key = np.asarray(key, dtype=np.float64)
    value = np.asarray(value, dtype=np.float64)
    if any(array.ndim != 2 for array in (query, key, value)):
        raise ValueError('query, key and value must be rank-two matrices')
    if query.shape[1] == 0 or query.shape[1] != key.shape[1]:
        raise ValueError('query and key feature widths must match and be positive')
    if key.shape[0] == 0 or key.shape[0] != value.shape[0]:
        raise ValueError('every key must have one value row')
    if not all(np.isfinite(array).all() for array in (query, key, value)):
        raise ValueError('finite inputs required')
    if allowed is None:
        allowed = np.ones((query.shape[0], key.shape[0]), dtype=bool)
    else:
        allowed = np.asarray(allowed)
        if allowed.dtype != np.bool_ or allowed.shape != (query.shape[0], key.shape[0]):
            raise ValueError('allowed must be a Boolean query-by-key matrix')
    if not allowed.any(axis=-1).all():
        raise ValueError('each query needs at least one allowed key')
    scores = query @ key.T / np.sqrt(query.shape[-1])
    masked_scores = np.where(allowed, scores, -np.inf)
    shifted_scores = masked_scores - masked_scores.max(axis=-1, keepdims=True)
    mass = np.exp(shifted_scores)
    weights = mass / mass.sum(axis=-1, keepdims=True)
    output = weights @ value
    return scores, weights, output


def attention(query, key, value, allowed=None):
    return attention_parts(query, key, value, allowed)[2]


def layer_norm(values, epsilon=1e-5):
    values = np.asarray(values, dtype=np.float64)
    if values.ndim < 1 or values.shape[-1] == 0:
        raise ValueError('a nonempty feature axis is required')
    if not np.isfinite(values).all() or not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError('finite inputs and positive finite epsilon are required')
    mean = values.mean(axis=-1, keepdims=True)
    variance = ((values - mean) ** 2).mean(axis=-1, keepdims=True)
    return (values - mean) / np.sqrt(variance + epsilon)


def verify():
    # Exercise 1: Permute content-only attention
    query = np.array([[1., 0.], [0., 1.], [1., 1.]])
    value = np.array([[1., 2.], [3., 4.], [5., 6.]])
    order = np.array([2, 0, 1])
    scores, weights, original = attention_parts(query, query, value)
    changed = attention(query[order], query[order], value[order])
    np.testing.assert_allclose(changed, original[order], atol=1e-12, rtol=0)
    scale = np.exp(1 / np.sqrt(2))
    expected_first_weights = np.array([scale, 1, scale]) / (2 * scale + 1)
    np.testing.assert_allclose(weights[0], expected_first_weights, atol=1e-12, rtol=0)
    np.testing.assert_allclose(original[0], [3, 4], atol=1e-12, rtol=0)
    assert scores.shape == weights.shape == (3, 3)
    assert original.shape == (3, 2)

    # Exercise 2: Normalize each token
    values = np.array([[1., 3.], [10., 20.]])
    changed = values.copy()
    changed[1] = [1000., 2000.]
    normalized = layer_norm(values)
    expected_first = np.array([-1., 1.]) / np.sqrt(1 + 1e-5)
    np.testing.assert_allclose(normalized[0], expected_first, atol=1e-12, rtol=0)
    np.testing.assert_allclose(layer_norm(changed)[0], normalized[0], atol=1e-12, rtol=0)
    assert normalized.shape == values.shape

    # Exercise 3: Expose sequence-wide leakage
    values = np.array([[1., 3.], [10., 20.]])
    changed = values.copy()
    changed[1] = [1000., 2000.]
    original_first = (values - values.mean(axis=0, keepdims=True))[0]
    changed_first = (changed - changed.mean(axis=0, keepdims=True))[0]
    np.testing.assert_array_equal(original_first, [-4.5, -8.5])
    np.testing.assert_array_equal(changed_first, [-499.5, -998.5])
    assert not np.allclose(original_first, changed_first)

    # Exercise 4: Attach fixed positions
    query = np.array([[1., 0.], [0., 1.], [1., 1.]])
    value = np.array([[1., 2.], [3., 4.], [5., 6.]])
    positions = np.array([[0., 0.], [1., 0.], [0., 2.]])
    order = np.array([2, 0, 1])
    original = attention(query + positions, query + positions, value)
    fixed_positions = attention(query[order] + positions, query[order] + positions, value[order])
    assert not np.allclose(fixed_positions, original[order])
    relabelled = attention((query + positions)[order], (query + positions)[order], value[order])
    np.testing.assert_allclose(relabelled, original[order], atol=1e-12, rtol=0)

    # Exercise 5: Check feature centering and causal prefixes
    values = np.array([[1., 2., 5.], [10., 20., 15.], [7., 0., -2.]])
    normalized = layer_norm(values)
    np.testing.assert_allclose(normalized.mean(axis=-1), 0, atol=1e-12, rtol=0)
    allowed = np.tri(len(values), dtype=bool)
    full = attention(normalized, normalized, normalized, allowed)
    for length in [1, 2, 3]:
        prefix = layer_norm(values[:length])
        result = attention(prefix, prefix, prefix, np.tri(length, dtype=bool))
        np.testing.assert_allclose(result, full[:length], atol=1e-12, rtol=0)
    order = np.array([2, 0, 1])
    permuted = normalized[order]
    fixed_mask = attention(permuted, permuted, permuted, allowed)
    assert not np.allclose(fixed_mask, full[order])

    # Exercise 6: Handle constant tokens and invalid normalization
    constant = layer_norm(np.array([[5., 5.]]))
    np.testing.assert_array_equal(constant, [[0., 0.]])
    assert np.isfinite(constant).all()
    for operation in [
        lambda: layer_norm(np.empty((2, 0))),
        lambda: layer_norm(np.array([[5., 5.]]), epsilon=0),
        lambda: attention(np.ones((1, 2)), np.ones((1, 2)), np.ones((1, 2)), np.zeros((1, 1), dtype=bool)),
    ]:
        try:
            operation()
        except ValueError:
            pass
        else:
            raise AssertionError('invalid contract was accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
