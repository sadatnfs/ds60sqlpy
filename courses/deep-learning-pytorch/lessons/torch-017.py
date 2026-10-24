"""torch-017: Dropout, regularization, train and eval modes.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate two penalties
# Use weights 1, -2 and compute L1 and squared L2 sums.
# Expected: L1=3; squared L2=5.

# Exercise 2: Check evaluation dropout
# Apply Dropout.5 in eval mode to ones twice.
# Expected: both outputs exactly ones.

# Exercise 3: Check training invariants
# Switch the same layer to train mode and inspect output values.
# Expected: shape(4, 8); only 0 or2.

# Exercise 4: Separate data and penalty terms
# Combine data loss 2 with coefficient.1 times squared L2.
# Expected: penalty.5; total 2.5.

# Exercise 5: Differentiate the explicit penalty
# Differentiate .1*sum(v*v) at v=[1, -2].
# Expected: gradient [.2, -.4].

# Exercise 6: Keep mode separate from gradients
# Set Dropout to eval and pass a requires_grad input.
# Expected: output still requires grad; backward gives ones.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
