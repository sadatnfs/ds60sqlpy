"""torch-026: Custom modules, residual paths, buffers and autograd checks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Build an identity residual
# Create a width 2 residual with zero kernel and scale buffer 1.
# Expected: output equals input; one parameter and one buffer.

# Exercise 2: Keep state stable across calls
# Call the same module on a second batch with the same width.
# Expected: same kernel object and parameter count 4.

# Exercise 3: Check a known residual transform
# Assign an identity kernel and scale.5.
# Expected: output 1.5*x.

# Exercise 4: Reject incompatible feature width
# Pass a width 3 row to the width 2 module.
# Expected: ValueError naming feature width.

# Exercise 5: Validate a custom cube derivative
# Run grad check on Cube.apply at float64 values.2, -.7.
# Expected: grad check True.

# Exercise 6: Inspect the incoming-gradient factor
# Differentiate the sum of 2*Cube(x) atx 2.
# Expected: gradient 24.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
