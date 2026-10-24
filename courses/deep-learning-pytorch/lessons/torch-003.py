"""torch-003: Linear modules, parameters and matrix contracts.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate a known affine layer
# UseX[[1, 2, 3], [0, 1, 0]], weight[[1, 0, -1]], bias 2.
# Expected: outputs[[0], [2]], shape(2, 1).

# Exercise 2: Inspect registered state
# Count weight and bias scalar entries and inspect state_dict keys.
# Expected: 4 scalars; keys weight, bias.

# Exercise 3: Compare with a mathematical matrix
# Transpose the stored weight and calculate X@W+b directly.
# Expected: direct result equals module output.

# Exercise 4: Remove the intercept explicitly
# Create a bias-free layer with the same stored weights.
# Expected: 3 parameters; outputs-2 and 0.

# Exercise 5: Expose an unregistered tensor
# Compare a Module holding a plain requires_grad tensor with one holding Parameter.
# Expected: plain module has 0 registered parameters; proper module has 1.

# Exercise 6: Reject wrong feature width
# Pass a2-feature row to the 3-input layer.
# Expected: RuntimeError from incompatible matrix dimensions.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
