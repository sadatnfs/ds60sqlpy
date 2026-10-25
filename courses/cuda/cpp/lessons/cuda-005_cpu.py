"""cuda-005: answer-free CPU model practice."""

# CPU model practice: Memory as addresses, ownership, shape and stride
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Compute the byte offset of (2,3) in a padded
# float64 matrix with row stride 8.
# Check the boundary from Exercise 5: What changes for a one-column matrix with padding?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

rows, cols, stride, itemsize = 2, 3, 5, 4
storage = [1, 2, 3, 4, 5, 6]

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
