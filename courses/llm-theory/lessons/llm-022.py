"""llm-022: Reproducibility, evaluation mode and restart.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Create Adam history
# Take two float32 Adam updates of(w-2)² fromw0.
# Expected: positive weight and optimizer step2.

# Exercise 2: Save a trusted local checkpoint
# Write the scalar weight and optimizer state into an owned temporary file.
# Expected: checkpoint file exists.

# Exercise 3: Calculate the uninterrupted next step
# Take one more update and save the expected weight.
# Expected: step3 and changed weight.

# Exercise 4: Restore in a new interpreter
# Load the trusted checkpoint into fresh weight and Adam objects, then take one step.
# Expected: child weight agrees within1e-6.

# Exercise 5: Expose weights-only continuation
# Initialize a fresh optimizer at the saved weight and compare its next update.
# Expected: weight differs from full-state continuation.

# Exercise 6: Verify evaluation and cleanup
# Use Dropout(.5) in eval mode on ones and remove only the owned temporary checkpoint.
# Expected: dropout returns ones; temporary path absent.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
