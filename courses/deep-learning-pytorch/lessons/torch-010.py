"""torch-010: Datasets, held-out families and leakage controls.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Inspect a literal Dataset
# Create eight records with groups A, A, B, B, C, C, D, D and values 1, 3, 5, 7, 20, 22,
# 30, 32.
# Expected: length 8; item 0 has ID 0, group A, value 1.

# Exercise 2: Select whole groups
# Train on accounts A, B and holdout C, D using Subset.
# Expected: four records each; group intersection empty.

# Exercise 3: Fit only training values
# Calculate the mean from the four training tensors.
# Expected: mean 4.

# Exercise 4: Perturb only assessment values
# Replace the final held-out value with 3200 in a copied dataset and recompute the
# training mean.
# Expected: training mean unchanged 4; global mean changes.

# Exercise 5: Expose row-level leakage
# Assign alternating indices to train/test and inspect group intersection.
# Expected: allA, B, C, D cross.

# Exercise 6: Apply the frozen transform
# Center held-out values with the training mean.
# Expected: 16, 18, 26, 28.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
