"""tf-032: Saving, export and inference parity.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Create a fixed inference model
# Set a bias-free Dense weight to2 and predict on1,3.
# Expected: predictions2,6.

# Exercise 2: Round-trip .keras
# Save and reload the model in a temporary directory.
# Expected: reloaded predictions match within1e-6.

# Exercise 3: Export an inference endpoint
# Call model.export into a different temporary subdirectory and load SavedModel.
# Expected: serve returns the same predictions.

# Exercise 4: Check both in a fresh process
# Load the .keras model and exported endpoint in a child interpreter and compare their
# outputs.
# Expected: both child outputs[[2],[6]].

# Exercise 5: Check a new batch length
# Use three valid rows instead of two with the restored model.
# Expected: output shape(3,1), predictions0,4,8.

# Exercise 6: Remove only owned artifacts
# Clean the temporary directory and check both artifacts are absent.
# Expected: temporary directory absent.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
