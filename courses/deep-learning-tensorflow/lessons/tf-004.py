"""tf-004: predict from the companion guide, then modify an owned copy."""

import numpy as np

r = np.array([1.0, -1.0, 2.0])
squared = np.square(r)
assert squared.sum() == 6.0
assert squared.mean() == 2.0
print(squared, squared.sum(), squared.mean())

include = np.array([True, True, False])
correct = np.square(r[include]).mean()
wrong = np.where(include, np.square(r), 0.0).mean()
assert correct == 1.0
np.testing.assert_allclose(wrong, 2 / 3, rtol=0, atol=1e-12)
print(correct, wrong)

# Exercise 1: Trace squared units
# Calculate the residual squares, sum, mean and root mean square for [1,-1,2].
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Duplicate the batch
# Append a second copy of all three residuals without changing their values.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Construct a masked reduction
# Implement reduce_squared with mean/sum choices and an optional boolean mask; include
# only the first two fixture entries.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Reject an absent objective
# Try an empty vector, an all-false mask, an integer mask and reduction name median.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Compare objective preferences
# Model A has residuals [0,0,4] and B has [2,2,2]. Compare mean squared and mean absolute
# errors.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Transfer to unequal groups
# Group A has one residual [2]; group B has three residuals [0,0,0]. Compare the all-
# record MSE with an unweighted mean of group MSEs.
# Add your attempt and keep its observed values or exception beside your prediction.
