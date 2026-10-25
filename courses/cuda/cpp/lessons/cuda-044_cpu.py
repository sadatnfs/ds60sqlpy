"""cuda-044: answer-free CPU model practice."""

# CPU model practice: Second capstone: a streaming numerical service core
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Write legal transitions for a two-slot
# pipeline.
# Check the boundary from Exercise 5: What should happen to a zero-length chunk?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

states = ["free", "filling", "computing", "copying", "consumed", "free"]
chunks = [[1, 2], [3], [], [4, 5]]

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
