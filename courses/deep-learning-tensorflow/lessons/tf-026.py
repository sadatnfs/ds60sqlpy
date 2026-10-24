"""tf-026: Custom layers, residuals and trainable state.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Create an identity residual
# Call a width2 residual with zero kernel on[[1,2],[3,4]].
# Expected: output equals input; one tracked kernel.

# Exercise 2: Reuse the state
# Call the layer on another batch of the same width and compare variable object identity.
# Expected: same variable object and variable count1.

# Exercise 3: Assign a known transform
# Set the kernel to identity and inspect the residual output.
# Expected: output2*x.

# Exercise 4: Reject an incompatible width
# Call the built width2 layer with a width3 input.
# Expected: ValueError naming feature width.

# Exercise 5: Check branch gradients
# Differentiate the sum of output entries with respect to the kernel.
# Expected: gradient matrix[[4,4],[6,6]].

# Exercise 6: Count parameters by width
# Build a separate width3 layer and count its square kernel entries.
# Expected: 9 parameters; width2 layer remains4.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
