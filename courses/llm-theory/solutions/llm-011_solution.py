"""llm-011: bounded local reference checks. No network or persistent data writes."""

import numpy as np

def split_heads(values, heads):
    values = np.asarray(values)
    if values.ndim != 2 or min(values.shape) == 0:
        raise ValueError('nonempty token-by-feature input required')
    if type(heads) is not int or heads <= 0 or values.shape[1] % heads != 0:
        raise ValueError('positive head count must divide feature width')
    time, width = values.shape
    head_width = width // heads
    return values.reshape(time, heads, head_width).transpose(1, 0, 2)


def join_heads(values):
    values = np.asarray(values)
    if values.ndim != 3 or min(values.shape) == 0:
        raise ValueError('nonempty head-by-token-by-feature input required')
    heads, time, head_width = values.shape
    return values.transpose(1, 0, 2).reshape(time, heads * head_width)


def multihead(values, heads=2, causal=True):
    values = np.asarray(values, dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError('finite values required')
    projected = split_heads(values, heads)
    head_width = projected.shape[-1]
    scores = projected @ projected.transpose(0, 2, 1) / np.sqrt(head_width)
    time = values.shape[0]
    allowed = np.tri(time, dtype=bool) if causal else np.ones((time, time), dtype=bool)
    masked = np.where(allowed[None, :, :], scores, -np.inf)
    mass = np.exp(masked - masked.max(axis=-1, keepdims=True))
    weights = mass / mass.sum(axis=-1, keepdims=True)
    head_outputs = weights @ projected
    return join_heads(head_outputs), weights


def tokenwise_feed_forward(values):
    values = np.asarray(values, dtype=np.float64)
    width = values.shape[-1]
    first_weight = np.eye(width)
    first_bias = np.full(width, -2.0)
    second_weight = np.eye(width)
    hidden = np.maximum(values @ first_weight + first_bias, 0)
    return hidden @ second_weight


def verify():
    # Exercise 1: Split and rejoin
    values = np.arange(8).reshape(2, 4)
    heads = split_heads(values, 2)
    np.testing.assert_array_equal(heads[0], [[0, 1], [4, 5]])
    np.testing.assert_array_equal(heads[1], [[2, 3], [6, 7]])
    np.testing.assert_array_equal(join_heads(heads), values)
    assert heads.shape == (2, 2, 2)

    # Exercise 2: Calculate a residual
    values = np.arange(8).reshape(2, 4)
    branch = 2 * values
    residual = values + branch
    np.testing.assert_array_equal(residual, 3 * values)
    np.testing.assert_array_equal(values + np.zeros_like(values), values)
    np.testing.assert_array_equal(values + (-values), np.zeros_like(values))
    assert residual.shape == values.shape

    # Exercise 3: Use a tokenwise nonlinear block
    values = np.arange(8, dtype=np.float64).reshape(2, 4)
    output = tokenwise_feed_forward(values)
    np.testing.assert_array_equal(output[0], [0, 0, 0, 1])
    changed = values.copy()
    changed[1] = [100, 200, 300, 400]
    np.testing.assert_array_equal(tokenwise_feed_forward(changed)[0], output[0])

    # Exercise 4: Test actual head mixtures and causal prefixes
    values = np.array([[1., 0., 1., 1.], [0., 1., 1., 0.], [1., 1., 0., 1.]])
    output, weights = multihead(values, heads=2, causal=True)
    a = np.exp(1 / np.sqrt(2))
    np.testing.assert_allclose(weights[0, 1, :2], [1 / (1 + a), a / (1 + a)], atol=1e-12, rtol=0)
    np.testing.assert_allclose(weights[1, 1, :2], [0.5, 0.5], atol=1e-12, rtol=0)
    np.testing.assert_array_equal(weights[:, 1, 2], [0, 0])
    np.testing.assert_allclose(output[1], [1 / (1 + a), a / (1 + a), 1, 0.5], atol=1e-12, rtol=0)
    for length in [1, 2, 3]:
        prefix, _ = multihead(values[:length], heads=2, causal=True)
        np.testing.assert_allclose(prefix, output[:length], atol=1e-12, rtol=0)

    # Exercise 5: Reject an indivisible width
    for values, count in [(np.zeros((2, 5)), 2), (np.zeros((2, 4)), 0), (np.zeros((0, 4)), 2)]:
        try:
            split_heads(values, count)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid head layout accepted')

    # Exercise 6: Detect a wrong rejoin
    values = np.arange(8).reshape(2, 4)
    heads = split_heads(values, 2)
    wrong = heads.reshape(2, 4)
    np.testing.assert_array_equal(wrong, [[0, 1, 4, 5], [2, 3, 6, 7]])
    assert wrong.shape == values.shape
    assert not np.array_equal(wrong, values)
    np.testing.assert_array_equal(join_heads(heads), values)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
