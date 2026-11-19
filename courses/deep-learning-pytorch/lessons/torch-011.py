"""torch-011: nn.Module, registered parameters and explicit training loops.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Evaluate a module with a nonzero buffer
# Build ScalarModel, set its offset buffer to 1 under no_grad and evaluate x = 1, 2, 3.
# Expected: outputs [1, 1, 1]; offset is a buffer, not a parameter.

# Exercise 2: Predict one step with the offset present
# Train the shifted module one SGD step with learning rate 0.1 toward y = 2x using mean
# squared error.
# Expected: initial loss 35/3; new weight 22/15; offset still 1.

# Exercise 3: Count state in a ModuleList
# Put two ScalarModel instances in nn.ModuleList and count parameters, buffers and
# state_dict keys.
# Expected: 2 parameters, 2 buffers and keys 0.weight, 0.offset, 1.weight, 1.offset.

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
