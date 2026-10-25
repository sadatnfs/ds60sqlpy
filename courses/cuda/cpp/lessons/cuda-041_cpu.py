"""cuda-041: answer-free CPU model practice."""

# CPU model practice: Stream-ordered allocation and memory pools
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Name both event dependencies in the cross-
# stream example.
# Check the boundary from Exercise 5: What should allocation failure preserve?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

events = [
    "allocate_A",
    "write_A",
    "ready",
    "wait_ready_B",
    "read_B",
    "done",
    "wait_done_A",
    "free_A",
]
reserved_mib, live_mib = 64, 0

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
