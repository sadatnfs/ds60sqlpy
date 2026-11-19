"""torch-020: Pooling, local augmentation and label invariants.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Pool a new patch
# Pool the patch [[5, -1], [2, 6]] with a 2-by-2 window.
# Expected: max 6; average 3.

# Exercise 2: Flip the height axis instead
# Flip the same patch along the height axis and read its rows.
# Expected: rows [2, 6] and [5, -1].

# Exercise 3: Pool a 4-by-4 map
# Apply 2-by-2 max and average pooling to the 4-by-4 map with values 0..15.
# Expected: max [[5, 7], [13, 15]]; average [[2.5, 4.5], [10.5, 12.5]].

# Exercise 4: Expose discarded information
# Change only the non-maximum pixel 1 to 0 and compare both pools.
# Expected: max still 4; average 2.25.

# Exercise 5: Keep evaluation transforms deterministic
# Define a transform that flips only in training and returns an owned copy in evaluation.
# Expected: evaluation equals source and does not alias it.

# Exercise 6: Transform directional labels consistently
# Map left to right under horizontal reflection and check the inverse.
# Expected: left->right->left.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
