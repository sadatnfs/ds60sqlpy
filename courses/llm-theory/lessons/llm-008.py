"""llm-008: predict from the companion guide, then modify an owned copy."""

import numpy as np

table = np.array([[1, 0], [0, 1], [2, 2], [-1, 1]], dtype=np.float64)
ids = np.array([2, 0, 2], dtype=np.int64)
output = table[ids]
np.testing.assert_array_equal(output, [[2, 2], [1, 0], [2, 2]])
assert output.shape == (3, 2)
print(output)

wrapped = table[np.array([-1])]
np.testing.assert_array_equal(wrapped, [[-1, 1]])
assert int(np.array([-1])[0]) < 0
print(wrapped)

# Exercise 1: Trace row selection
# Calculate the output for IDs [2,0,2] from the supplied four-row table.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct a lookup guard
# Implement lookup(table,ids) and compare its result with a one-hot matrix product.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Reject invalid IDs
# Test IDs [-1], [4] and [1.5] without allowing negative wrap or rounding.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Handle an empty token list
# Look up [] in the same nonempty table and state which later stage must decide whether
# empty text is acceptable.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Preserve table ownership
# Change output[0,0] to 999 after lookup, then inspect the original table and the repeated
# third output row.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Transfer across a vocabulary permutation
# Reorder table rows using [2,0,3,1]. Remap the original IDs [2,0,2] so their feature
# vectors stay identical.
# Add your attempt and keep its observed values or exception beside your prediction.
