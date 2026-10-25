"""cuda-061: answer-free CPU model practice."""

# CPU model practice: From one pad to a maintainable CUDA project
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Name source and build directories in a clean
# out-of-source project.
# Check the boundary from Exercise 5: What does a successful CMake configure prove?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

project = {
    "include/transform.hpp": "host interface",
    "src/transform.cu": "kernel and launcher",
    "src/main.cpp": "fixture and validation",
    "build/": "generated artifacts",
}

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
