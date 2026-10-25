"""cuda-056: answer-free CPU model practice."""

# CPU model practice: Asynchronous copies, barriers and software pipelines
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: List the lifetime states of one tile slot.
# Check the boundary from Exercise 5: What happens to a partial final tile?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

states = ["free", "copying", "ready", "consuming", "done", "free"]

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
