"""cuda-008: answer-free CPU model practice."""

# CPU model practice: Reproducibility, safety and the first evidence notebook
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Write five required fields for a correctness
# receipt.
# Check the boundary from Exercise 5: How should a no-device run be represented?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

x, y = [0, -2, 5], [3, 2, -1]
receipt = {"surface": "CPU reference", "shape": [3], "result": [3, 0, 4], "gpu_executed": False}

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
