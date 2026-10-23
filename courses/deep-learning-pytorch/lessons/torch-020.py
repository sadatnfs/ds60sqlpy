"""torch-020: Pooling, local augmentation and label invariants.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare local reductions
# Pool patch 1, 3; 2, 4 with a 2-by-2 window.
# Expected: max 4; average 2.5.

# Exercise 2: Inspect a horizontal flip
# Flip the width axis and read the pixel s.
# Expected: rows 3, 1 and 4, 2.

# Exercise 3: Check the round trip
# Flip the image horizontal l y twice.
# Expected: exact original values.

# Exercise 4: Expose discarded information
# Change only the non maximum pixel 1 to0 and compare pool s.
# Expected: max still 4; average 2.25.

# Exercise 5: Keep evaluation transforms deterministic
# Define a transform that flips only in training and returns an owned copy in evaluation.
# Expected: evaluation equals source and does not alias it.

# Exercise 6: Transform directional labels consistently
# Map left to right under horizontal reflect i on and check the inverse.
# Expected: left->right->left.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
