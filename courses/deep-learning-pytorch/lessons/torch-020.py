"""torch-020: Pooling, local augmentation and label invariants.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare local reductions
# Pool patch1, 3; 2, 4 with a2 x2 window.
# Expected: max4; average2.5.

# Exercise 2: Inspect a horizontal flip
# Flip the width axis and read the pixel s.
# Expected: rows3, 1 and4, 2.

# Exercise 3: Check the round trip
# Flip the image horizontal l y twice.
# Expected: exact original values.

# Exercise 4: Expose discarded information
# Change only the non maximum pixel1 to0 and compare pool s.
# Expected: max still4; average2.25.

# Exercise 5: Keep evaluation transforms deterministic
# Define a transform that flips only in training and returns an owned copy in evaluation.
# Expected: evaluation equals source and does not alias it.

# Exercise 6: Transform directional labels consistently
# Map left to right under horizontal reflect i on and check the inverse.
# Expected: left->right->left.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
