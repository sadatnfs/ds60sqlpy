"""An inspectable NumPy decoder forward pass; no pretrained assets or network."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]
EMBEDDINGS = np.array(
    [
        [1.0, 0.0, -1.0, 0.0],
        [0.0, 1.0, 0.0, -1.0],
        [1.0, 1.0, 0.0, -1.0],
        [-1.0, 0.0, 1.0, 1.0],
    ]
)
POSITIONS = np.array(
    [
        [0.0, 0.0, 0.0, 0.0],
        [0.1, 0.0, -0.1, 0.0],
        [0.0, 0.1, 0.0, -0.1],
        [-0.1, 0.1, 0.1, -0.1],
    ]
)
VOCABULARY = ("red", "fox", "runs", "<end>")


def softmax(scores: Array, allowed: NDArray[np.bool_] | None = None) -> Array:
    """Normalize over the last axis, rejecting a query with no legal keys."""
    if not np.isfinite(scores).all():
        raise ValueError("Scores must be finite before masking")
    if allowed is not None:
        if allowed.shape != scores.shape or not allowed.any(axis=-1).all():
            raise ValueError("Every query needs at least one legal key")
        scores = np.where(allowed, scores, -np.inf)
    weights = np.exp(scores - scores.max(axis=-1, keepdims=True))
    return weights / weights.sum(axis=-1, keepdims=True)


def layer_norm(x: Array) -> Array:
    """Normalize each token's features, never across different token positions."""
    return (x - x.mean(axis=-1, keepdims=True)) / np.sqrt(
        x.var(axis=-1, keepdims=True) + 1e-5
    )


def forward(ids: list[int], output_weights: Array) -> tuple[Array, Array, Array]:
    """One pre-normalized decoder block with two heads of width two."""
    if not ids or len(ids) > len(POSITIONS):
        raise ValueError("Use one to four token IDs")
    if any(type(token) is not int or not 0 <= token < len(VOCABULARY) for token in ids):
        raise ValueError("Token IDs must belong to this vocabulary")
    if output_weights.shape != (4, 4) or not np.isfinite(output_weights).all():
        raise ValueError("The output projection must be a finite 4 by 4 matrix")
    x = EMBEDDINGS[ids] + POSITIONS[: len(ids)]
    normalized = layer_norm(x)
    length = len(ids)
    # Identity Q/K/V/output projections keep the arithmetic small. They are
    # trainable, generally different matrices in a trained decoder.
    q = normalized.reshape(length, 2, 2).transpose(1, 0, 2)
    k = q.copy()
    v = q.copy()
    scores = q @ k.transpose(0, 2, 1) / np.sqrt(2.0)
    legal = np.broadcast_to(
        np.tril(np.ones((length, length), dtype=bool)), scores.shape
    )
    attention = softmax(scores, legal)
    mixtures = attention @ v
    joined = mixtures.transpose(1, 0, 2).reshape(length, 4)
    residual = x + joined
    # A fixed pointwise nonlinear map makes the residual MLP explicit without
    # hiding a large random parameter table in the walkthrough.
    hidden = np.maximum(layer_norm(residual), 0.0)
    residual = residual + 0.2 * hidden
    final = layer_norm(residual)
    return final @ output_weights, attention, final


def loss(logits: Array, targets: list[int]) -> float:
    if logits.ndim != 2 or logits.shape[0] != len(targets) or not targets:
        raise ValueError("One target is required for each logits row")
    if any(
        type(target) is not int or not 0 <= target < logits.shape[1]
        for target in targets
    ):
        raise ValueError("Target IDs must belong to the output vocabulary")
    shifted = logits - logits.max(axis=-1, keepdims=True)
    log_probabilities = shifted - np.log(np.exp(shifted).sum(axis=-1, keepdims=True))
    return float(-log_probabilities[np.arange(len(targets)), targets].mean())


def main() -> None:
    # Predict fox after red, runs after red/fox, and end after red/fox/runs.
    ids, targets = [0, 1, 2], [1, 2, 3]
    output_weights = EMBEDDINGS.T.copy()
    logits, attention, features = forward(ids, output_weights)
    assert logits.shape == (3, 4) and attention.shape == (2, 3, 3)
    np.testing.assert_allclose(attention.sum(axis=-1), 1.0, atol=1e-12, rtol=0)
    assert np.all(attention[:, np.triu_indices(3, 1)[0], np.triu_indices(3, 1)[1]] == 0)
    prefix_logits, _, _ = forward(ids[:2], output_weights)
    np.testing.assert_allclose(prefix_logits, logits[:2], atol=1e-12, rtol=0)
    altered_logits, _, _ = forward([0, 1, 3], output_weights)
    np.testing.assert_allclose(altered_logits[:2], logits[:2], atol=1e-12, rtol=0)

    probabilities = softmax(logits)
    before = loss(logits, targets)
    # Exact cross-entropy gradient for the output head, with features frozen.
    error = probabilities.copy()
    error[np.arange(3), targets] -= 1.0
    gradient = features.T @ error / len(targets)
    epsilon = 1e-6
    plus, minus = output_weights.copy(), output_weights.copy()
    plus[0, 1] += epsilon
    minus[0, 1] -= epsilon
    numerical = (loss(features @ plus, targets) - loss(features @ minus, targets)) / (
        2 * epsilon
    )
    np.testing.assert_allclose(numerical, gradient[0, 1], atol=1e-8, rtol=0)
    after = loss(features @ (output_weights - 0.05 * gradient), targets)
    assert after < before
    try:
        softmax(np.zeros((1, 2)), np.zeros((1, 2), dtype=bool))
    except ValueError:
        pass
    else:
        raise AssertionError("An all-masked query must be rejected")
    np.set_printoptions(precision=6, suppress=True)
    print("Vocabulary:", VOCABULARY)
    print("Head 0 attention:\n", attention[0])
    print("Last-position next-token probabilities:", probabilities[-1])
    print(f"Mean loss before/after one output-head update: {before:.6f} / {after:.6f}")
    print(
        "PASS: legal attention, prefix invariance, finite-difference gradient, descending loss"
    )


if __name__ == "__main__":
    main()
