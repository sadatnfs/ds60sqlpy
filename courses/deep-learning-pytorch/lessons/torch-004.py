"""torch-004: Loss functions, reductions and gradient scale.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Reduce a new residual vector
# Use residuals [3, 0, -1, 2] against zero targets and compute the sum and mean squared
# reductions.
# Expected: squared entries 9, 0, 1, 4; sum 14; mean 3.5.

# Exercise 2: Predict the effect of an appended zero
# Append one zero residual to the same vector and recompute both reductions before running
# them.
# Expected: sum stays 14; mean falls to 2.8 because the denominator becomes 5.

# Exercise 3: Compare gradient scale for four entries
# Differentiate the sum and the mean of squares for a fresh copy of [3, 0, -1, 2].
# Expected: sum gradient [6, 0, -2, 4]; it equals 4 times the mean gradient.

# Exercise 4: Inspect a feature denominator
# Use a 2-by-2 residual matrix of ones and mean reduction.
# Expected: loss 1 and 4 participating elements.

# Exercise 5: Mask numerator and denominator together
# Use losses [1, 4, 100] with mask True, True, False.
# Expected: valid mean 2.5, not 5/3.

# Exercise 6: Separate a metric from the objective
# Compare mean absolute residual and mean squared residual for [1, -1, 2].
# Expected: MAE 4/3; MSE 2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
