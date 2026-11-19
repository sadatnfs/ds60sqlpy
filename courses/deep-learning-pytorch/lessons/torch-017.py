"""torch-017: Dropout, regularization, train and eval modes.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute penalties for a new vector
# Use weights 3, -4, 0 and compute the L1 and squared L2 sums.
# Expected: L1 = 7; squared L2 = 25.

# Exercise 2: Predict train-mode values for p=0.25
# Apply Dropout(0.25) in train mode to a (3, 5) tensor of ones and inspect every value.
# Expected: shape (3, 5); each value is 0 or 4/3.

# Exercise 3: Confirm eval disables the new rate
# Switch the same Dropout(0.25) layer to eval mode and apply it to the ones tensor.
# Expected: output exactly equals the input.

# Exercise 4: Separate data and penalty terms
# Combine data loss 2 with coefficient 0.1 times squared L2.
# Expected: penalty 0.5; total 2.5.

# Exercise 5: Differentiate the explicit penalty
# Differentiate 0.1*sum(v*v) at v=[1, -2].
# Expected: gradient [0.2, -0.4].

# Exercise 6: Keep mode separate from gradients
# Set Dropout to eval and pass a requires_grad input.
# Expected: output still requires grad; backward gives ones.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
