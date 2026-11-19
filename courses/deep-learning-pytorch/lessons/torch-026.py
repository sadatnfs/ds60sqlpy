"""torch-026: Custom modules, residual paths, buffers and autograd checks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Apply a swapping kernel
# Create Residual(2), set its kernel to [[0, 1], [1, 0]] and its scale buffer to 2, and
# evaluate the row [1, 2].
# Expected: output [[5, 4]].

# Exercise 2: Predict state for a wider module
# Create Residual(3) and count its parameter scalars and buffers.
# Expected: 9 kernel scalars and 1 buffer.

# Exercise 3: Differentiate Cube at a new point
# Backpropagate the sum of 3*Cube(x) at x = -1.
# Expected: gradient 9.

# Exercise 4: Reject incompatible feature width
# Pass a width 3 row to the width 2 module.
# Expected: ValueError naming feature width.

# Exercise 5: Validate a custom cube derivative
# Run gradcheck on Cube.apply at float64 values 0.2, -0.7.
# Expected: gradcheck returns True.

# Exercise 6: Inspect the incoming-gradient factor
# Differentiate the sum of 2*Cube(x) at x = 2.
# Expected: gradient 24.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
