"""tf-020: Pooling and augmentation without label leakage.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare two reductions
# Pool patch[[1,3],[2,4]] with a2x2 window.
# Expected: max4; average2.5.

# Exercise 2: Inspect a flip
# Flip the patch horizontally and inspect every pixel.
# Expected: rows[3,1] and[4,2].

# Exercise 3: Check an involution
# Flip twice and compare with the original image.
# Expected: all pixels restored exactly.

# Exercise 4: Expose discarded information
# Change the nonmaximum pixel1 to0 and recompute both pools.
# Expected: max still4; average2.25.

# Exercise 5: Keep evaluation deterministic
# Define evaluation as an identity transform and compare repeated results with the source.
# Expected: both evaluations equal the original patch.

# Exercise 6: Reject a semantic flip
# Encode labels left and right and define the label change caused by horizontal
# reflection.
# Expected: left maps to right; retaining left is invalid.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
