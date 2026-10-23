from __future__ import annotations

import math

import numpy as np


def fit_bigram(sequences, vocabulary):
    vocabulary = tuple(vocabulary)
    if not vocabulary or len(set(vocabulary)) != len(vocabulary):
        raise ValueError("unique nonempty vocabulary required")
    indices = {token: index for index, token in enumerate(vocabulary)}
    counts = np.zeros((len(vocabulary), len(vocabulary)), dtype=np.int64)
    for sequence in sequences:
        sequence = list(sequence)
        if any(token not in indices for token in sequence):
            raise ValueError("unknown training token")
        for left, right in zip(sequence, sequence[1:], strict=False):
            counts[indices[left], indices[right]] += 1
    return counts


def next_probabilities(counts, context, vocabulary):
    vocabulary = tuple(vocabulary)
    counts = np.asarray(counts)
    if not vocabulary or counts.shape != (len(vocabulary), len(vocabulary)):
        raise ValueError("vocabulary/count shape mismatch")
    if (counts < 0).any():
        raise ValueError("nonnegative counts required")
    row = counts[vocabulary.index(context)] if context in vocabulary else np.zeros(len(vocabulary))
    mass = np.asarray(row, dtype=np.float64) + 1
    return mass / mass.sum()


def verify():
    vocabulary = ("A", "B", "C")
    # Exercise 1: within-document counts
    counts = fit_bigram([["A", "B", "A"], ["A", "A"]], vocabulary)
    np.testing.assert_array_equal(counts, [[1, 1, 0], [1, 0, 0], [0, 0, 0]])
    # Exercise 2: explicit pseudo-count denominators
    for context, expected in (
        ("A", [2 / 5, 2 / 5, 1 / 5]),
        ("B", [0.5, 0.25, 0.25]),
        ("C", [1 / 3] * 3),
    ):
        np.testing.assert_allclose(
            next_probabilities(counts, context, vocabulary), expected, rtol=0, atol=1e-12
        )
    # Exercise 3: no cross-document pair
    assert fit_bigram([["A"], ["B"]], vocabulary).sum() == 0
    assert fit_bigram([["A", "B"]], vocabulary).sum() == 1
    # Exercise 4: an unseen context does not add vocabulary
    original = counts.copy()
    np.testing.assert_allclose(
        next_probabilities(counts, "Z", vocabulary), [1 / 3] * 3, rtol=0, atol=1e-12
    )
    # Exercise 5: invalid vocabulary or training token
    for documents, vocab in (([], []), ([], ["A", "A"]), ([["Z"]], vocabulary)):
        try:
            fit_bigram(documents, vocab)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid training fixture accepted")
    # Exercise 6: held-out scoring is read-only
    score = -math.log(next_probabilities(counts, "C", vocabulary)[0])
    assert math.isclose(score, math.log(3), rel_tol=0, abs_tol=1e-12)
    np.testing.assert_array_equal(counts, original)
    return {"transitions": int(counts.sum()), "validation_nll": score}


if __name__ == "__main__":
    print(verify())
