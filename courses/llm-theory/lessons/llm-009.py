"""llm-009: read the companion guide, predict, then edit your own copy."""

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


# Exercise 1: Trace three mixtures
# Draw the three allowed rows and calculate the output of Example A by hand before
# executing it. Label query and key axes.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 2: Change only the future
# Repeat Example B with the third value `[100,200]`. Keep Q, K and the first two value
# rows fixed. Explain which output rows may change under the causal contract.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 3: Construct a nonuniform prefix oracle
# Use `Q=K=[[1,0],[0,1],[1,1],[-1,1]]` and `V=[[1,2],[3,4],[5,6],[7,8]]`. For cuts 1
# through 4, compare the full result's early rows with an independently recomputed prefix.
# Then perturb only Q, K and V rows at positions 2 and later and compare the first two
# outputs.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 4: Diagnose a plausible-looking triangle
# For the zero-score three-token example, a broken implementation computes an unmasked
# softmax first and then multiplies it by the lower triangle without renormalizing.
# Calculate the resulting row sums and outputs, then repair the score/mask order.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 5: Make invalid inputs fail clearly
# Add tests for an empty token axis, an integer rather than boolean mask, a wrong mask
# shape, and an all-false second query row. Also try a NaN in V.
# Keep your prediction, code change and observed check in your own copy.

# Exercise 6: Transfer to next-token labels
# Given IDs `[2,5,7,3]`, construct the decoder inputs and next-token labels. Explain
# whether query zero may see its current input, whether it may see its target in the next
# input position, and one data-leakage failure that a correct mask does not address.
# Keep your prediction, code change and observed check in your own copy.

if __name__ == "__main__":
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
