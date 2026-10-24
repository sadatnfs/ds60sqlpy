"""torch-011: nn.Module, registered parameters and explicit training loops.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Inspect module state
# Build Scalar Model with weight 0 and buffer offset 0.
# Expected: one parameter weight; one buffer offset; both in state_dict.

# Exercise 2: Check a forward call
# Runx 1, 2, 3 through the zero-weight module.
# Expected: three zero outputs; weight unchanged.

# Exercise 3: Run one explicit loop step
# Use SGD with rate 0.1 and mean squared error, clearing gradients before backward.
# Expected: weight 28/15; buffer still 0.

# Exercise 4: Move dtype through registered state
# Convert the module to float32 and inspect parameter and buffer dtypes.
# Expected: both float32.

# Exercise 5: Expose stale optimizer membership
# Create an optimizer, replace the module Parameter, and inspect captured object identity.
# Expected: optimizer still holds old Parameter, not replacement.

# Exercise 6: Keep parameter count stable across calls
# Call a fresh module on batches of length 1 and 4 and compare parameter identities.
# Expected: same weight object and one parameter.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
