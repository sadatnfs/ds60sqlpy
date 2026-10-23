"""torch-004: Loss functions, reductions and gradient scale.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute residual reductions
# Use residuals[1, -1, 2] against zero targets.
# Expected: squared entries1, 1, 4; sum6; mean2.

# Exercise 2: Duplicate the batch
# Repeat every residual twice and compare reductions.
# Expected: sum12; mean2.

# Exercise 3: Compare derivative scale
# Differentiate sum and mean squared loss for a fresh3-entry tensor.
# Expected: sum gradient equals3 times mean gradient.

# Exercise 4: Inspect a feature denominator
# Use a2x2 residual matrix of ones and mean reduction.
# Expected: loss1 and4 participating elements.

# Exercise 5: Mask numerator and denominator together
# Use losses[1, 4, 100] with mask True, True, False.
# Expected: valid mean2.5, not5/3.

# Exercise 6: Separate a metric from the objective
# Compare mean absolute residual and mean squared residual for[1, -1, 2].
# Expected: MAE4/3; MSE2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
