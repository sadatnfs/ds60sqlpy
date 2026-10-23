"""torch-036: Capstone: release a small reproducible PyTorch model.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze the scalar experiment
# Use train x1, 2, 3 and holdout 4, 5 with target 2 x and disjoint IDs.
# Expected: 3training and 2 holdout records.

# Exercise 2: Train within a declared budget
# Zero-initialize float64 Linear and run 30 SGD.01 updates.
# Expected: finite weights; holdout error below constant training-mean baseline 26.

# Exercise 3: Build the owned release bundle
# Save weights, schema and split manifest with a weight SHA256.
# Expected: manifest has feature x, float64, width 1 and matching hash.

# Exercise 4: Verify fresh-process prediction parity
# Run the checked loader in a fresh interpreter and compare holdout predictions.
# Expected: predictions match within 1e-12.

# Exercise 5: Make a corrupted artifact fail
# Replace the declared weight hash with 64 zeros and rerun the loader.
# Expected: nonzero child exit and weight hash mismatch diagnostic.

# Exercise 6: Record a bounded decision and cleanup
# Record local parity pass, holdout count 2, previous artifact v1 and production no-go,
# then remove owned files.
# Expected: local checks True; production no-go; directory absent.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
