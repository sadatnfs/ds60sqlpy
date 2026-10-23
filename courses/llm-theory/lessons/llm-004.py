"""llm-004: predict from the companion guide, then modify an owned copy."""

import numpy as np

counts = np.array([[1, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.int64)
mass = counts + 1
probabilities = mass / mass.sum(axis=1, keepdims=True)
np.testing.assert_allclose(probabilities[0], [2 / 5, 2 / 5, 1 / 5], rtol=0, atol=1e-12)
np.testing.assert_allclose(probabilities.sum(axis=1), 1.0, rtol=0, atol=1e-12)
print(probabilities)

documents = [["A"], ["B"]]
pairs = [pair for document in documents for pair in zip(document, document[1:], strict=False)]
concatenated = ["A", "B"]
wrong_pairs = list(zip(concatenated, concatenated[1:], strict=False))
assert pairs == []
assert wrong_pairs == [("A", "B")]
print(pairs, wrong_pairs)

# Exercise 1: Trace training counts
# For vocabulary [A,B,C] and training [[A,B,A],[A,A]], list each within-sequence
# transition and fill the count matrix.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct a smoothed row
# Implement fit_bigram and next_probabilities using fixed vocabulary order and add-one
# smoothing.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Preserve document boundaries
# Fit two separate documents [A] and [B], then compare with one concatenated [A,B]
# document.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Handle an unseen context
# Request probabilities after Z without adding Z to the candidate vocabulary.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Reject malformed training data
# Try duplicate vocabulary entries, an empty vocabulary and an unknown training token Z.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Keep validation read-only
# Score the transition C-to-A from a validation document using the frozen table.
# Add your attempt and keep its observed values or exception beside your prediction.
