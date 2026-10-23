"""tf-003: predict from the companion guide, then modify an owned copy."""

import numpy as np

X = np.array([[1, 2, 3], [0, 1, 0]], dtype=np.float64)
W = np.array([[1], [0], [-1]], dtype=np.float64)
result = X @ W + 2
np.testing.assert_array_equal(result, [[0], [2]])
print(result)

wrong = X @ W + np.array([2, 3, 4])
assert wrong.shape == (2, 3)
np.testing.assert_array_equal(wrong, [[0, 1, 2], [2, 3, 4]])
print(wrong)

# Exercise 1: Trace the product
# Write all multiply/add terms for both rows of the first example, then execute it.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Add an observation
# Append row [3,0,0] to X without changing W or the bias.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Reject incompatible features
# Implement affine(X,W,bias), then pass a (2,3) X with a (2,1) W.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Guard the bias axis
# Reject bias [2,3,4] for the one-output model while accepting scalar 2 and output vector
# [2].
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Extend to two outputs
# Use W=[[1,0],[0,1],[-1,1]] and bias [2,-1] on the original X.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Preserve a prediction under unit conversion
# For X=[[100],[200]] centimeters, W=[[0.02]] and bias 1, convert X to meters and choose
# the corresponding new W.
# Add your attempt and keep its observed values or exception beside your prediction.
