"""llm-002: predict from the companion guide, then modify an owned copy."""

import numpy as np

for scores in ([0.0, 0.0], [1000.0, 1000.0]):
    values = np.asarray(scores, dtype=np.float64)
    mass = np.exp(values - values.max())
    probabilities = mass / mass.sum()
    np.testing.assert_allclose(probabilities, [0.5, 0.5], rtol=0, atol=1e-12)
    print(probabilities)

scores = np.array([0.0, 100.0, 0.0])
allowed = np.array([True, False, True])
masked = np.where(allowed, scores, -np.inf)
mass = np.exp(masked - masked.max())
probabilities = mass / mass.sum()
np.testing.assert_allclose(probabilities, [0.5, 0.0, 0.5], rtol=0, atol=1e-12)
print(probabilities)

# Exercise 1: Explain the shift
# Run both equal-score fixtures and derive why subtracting a shared offset preserves the
# ratio.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct a stable helper
# Implement softmax(scores,allowed=None) for a finite nonempty vector. Compare [0,log(3)]
# with the same vector plus 1000.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Preserve the legal candidate set
# Use [0,100,0] with mask [True,False,True], then explain why normalizing first and
# setting the middle result to zero is wrong.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Find a wrong reduction axis
# Take a 2x2 matrix of zero scores. Compare one global softmax with two independently
# normalized rows.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Reject invalid distributions
# Test an empty vector, a NaN score, an integer mask and an all-false boolean mask.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Transfer to temperature
# For scores [0,log(3)], divide by positive temperature 2 before softmax and compare the
# ranking with temperature 1.
# Add your attempt and keep its observed values or exception beside your prediction.
