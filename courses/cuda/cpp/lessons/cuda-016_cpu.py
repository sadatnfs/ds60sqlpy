"""cuda-016: answer-free CPU model practice."""

# CPU model practice: GPU memory spaces in one working program
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Assign storage for a reused image, a block
# tile and a scalar sum.
# Check the boundary from Exercise 5: Can one block read another block's ordinary shared
# array?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

placements = {"image": "global", "cooperative_tile": "shared", "sum": "thread local"}

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
