"""torch-010: Datasets, held-out families and leakage controls.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Inspect a different record
# Read item 5 of the literal Accounts dataset.
# Expected: ID 5, group C, value 22.

# Exercise 2: Hold out a different pair of groups
# Train on groups A and C and hold out B and D with Subset; check the group sets and the
# training mean.
# Expected: disjoint group sets; training mean 11.5.

# Exercise 3: Apply the new frozen transform
# Center the held-out values with the training mean 11.5.
# Expected: -6.5, -4.5, 18.5, 20.5.

# Exercise 4: Perturb only assessment values
# Replace the final held-out value with 3200 in a copied dataset and recompute the
# training mean.
# Expected: training mean unchanged 4; global mean changes.

# Exercise 5: Expose row-level leakage
# Assign alternating indices to train/test and inspect group intersection.
# Expected: all four account groups A, B, C and D cross the split.

# Exercise 6: Apply the frozen transform
# Center held-out values with the training mean.
# Expected: 16, 18, 26, 28.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
