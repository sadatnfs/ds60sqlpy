"""Tensor layout and tiled exact softmax, with no GPU performance claims."""

import numpy as np


def online_attention(scores, values, tile):
    maximum = -np.inf
    normalizer = 0.0
    numerator = np.zeros(values.shape[1])
    for start in range(0, len(scores), tile):
        part = scores[start : start + tile]
        vectors = values[start : start + tile]
        updated = max(maximum, float(part.max()))
        old_scale = np.exp(maximum - updated)
        weights = np.exp(part - updated)
        numerator = numerator * old_scale + weights @ vectors
        normalizer = normalizer * old_scale + weights.sum()
        maximum = updated
    return numerator / normalizer


def example_one():
    original = np.arange(24, dtype=np.float64).reshape(2, 3, 4)
    transposed = original.transpose(0, 2, 1)
    contiguous = np.ascontiguousarray(transposed)
    assert transposed.shape == contiguous.shape == (2, 4, 3)
    assert transposed.strides == (96, 8, 32)
    assert contiguous.strides == (96, 24, 8)
    np.testing.assert_array_equal(transposed, contiguous)
    print("Same values/shape, different byte strides:", transposed.strides, contiguous.strides)


def example_two():
    scores = np.array([1000.0, 1001.0, 998.0, 1003.0, 999.0])
    values = np.arange(10, dtype=float).reshape(5, 2)
    weights = np.exp(scores - scores.max())
    exact = weights @ values / weights.sum()
    for tile in (1, 2, 3, 5):
        np.testing.assert_allclose(online_attention(scores, values, tile), exact, atol=1e-12)
    print("Tiled online-softmax result:", exact)
    print("This is a CPU formula check, not a FlashAttention kernel or bandwidth benchmark.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
