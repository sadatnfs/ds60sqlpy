"""cuda-025: answer-free CPU model practice."""

# CPU model practice: A disciplined CUDA error taxonomy
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Classify an undefined reference to a host
# helper.
# Check the boundary from Exercise 5: What does a no-device status mean for a numerical
# test?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

failures = {
    "unknown identifier": "compile",
    "undefined reference": "link",
    "illegal access at completion": "execute",
    "wrong sum": "validate",
}

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
