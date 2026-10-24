"""llm-020: Initialization and residual scale.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Measure a small linear layer
# Apply.01*identity to input[1,-1,2,-2].
# Expected: output norm.01*sqrt10.

# Exercise 2: Increase only the scale
# Replace.01*identity with100*identity.
# Expected: activation norm increases by factor10000.

# Exercise 3: Trace gradients
# Differentiate mean squared output for the small and large matrices and compare norms.
# Expected: both finite; large-scale gradient norm is larger.

# Exercise 4: Find the first overflow
# Apply a float32 matrix scaled1e38, then inspect matrix product and squared loss.
# Expected: squared loss is nonfinite.

# Exercise 5: Repair on the same input
# Restore the small scale and recalculate output and loss for the unchangedx.
# Expected: both output and loss finite.

# Exercise 6: Check residual dimensions
# Compare residualx+x@small with an incompatible three-feature branch.
# Expected: valid residual shape(1,4); width3 branch rejected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
