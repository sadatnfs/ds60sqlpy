"""tf-002: predict from the companion guide, then modify an owned copy."""

import numpy as np

x = np.array([1, 2, 3], dtype=np.float64)
y = np.array([2, 4, 6], dtype=np.float64)
residual = x - y
assert residual.shape == (3,)
np.testing.assert_array_equal(residual, [-1, -2, -3])
print(residual)

column = y.reshape(3, 1)
grid = x - column
assert grid.shape == (3, 3)
np.testing.assert_array_equal(grid, [[-1, 0, 1], [-3, -2, -1], [-5, -4, -3]])
print(grid)

# Exercise 1: Trace compatible axes
# For the two worked examples, draw the observation axes and list all residual values
# before running subtraction.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct a paired subtraction guard
# Implement paired_difference(left,right) that explicitly converts to float64 but accepts
# only equal, nonempty vectors. Test the column target.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Diagnose an integer update
# Try subtracting 0.5 in place from an integer array [1,2,3]. Repair by creating an
# explicit floating copy without changing the original.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Reject absence and nonfinite data
# Test paired_difference on two empty vectors and on [1,NaN] versus [2,3]. Explain why a
# resulting NaN mean is not useful evidence.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Compare tolerance with exact text
# Form 0.1+0.2 using float64 and compare with 0.3. Choose an explicit absolute tolerance
# for this scalar check.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Transfer the unit contract
# Given heights [100,200] centimeters and targets [1,2] meters, convert the heights before
# paired subtraction.
# Add your attempt and keep its observed values or exception beside your prediction.
