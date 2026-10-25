"""cuda-026: answer-free CPU model practice."""

# CPU model practice: Compute Sanitizer as evidence, with its limits
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Choose a checker for an uninitialized global
# output read.
# Check the boundary from Exercise 5: Does a passing check at \(\mathrm{n}=32\)
# establish \(\mathrm{n}=33\) safety?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

n = 4
checker = {
    "out_of_bounds": "memcheck",
    "shared_hazard": "racecheck",
    "uninitialized": "initcheck",
    "invalid_barrier": "synccheck",
}

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
