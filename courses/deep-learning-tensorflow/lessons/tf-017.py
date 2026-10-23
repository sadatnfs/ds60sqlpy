"""tf-017: Regularization and training/evaluation behavior.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate penalties
# Compute L1 and squared L2 sums for weights[1,-2].
# Expected: L1=3; squaredL2=5.

# Exercise 2: Switch dropout to evaluation
# Apply dropout.5 twice to ones with training=False.
# Expected: both outputs equal the input.

# Exercise 3: Inspect training invariants
# Call the same dropout layer with training=True and examine allowed output values.
# Expected: shape(4,8), values only0 or2.

# Exercise 4: Separate objective terms
# Combine data loss2 with coefficient.1 times squaredL2 and report both components.
# Expected: data2, penalty.5, total2.5.

# Exercise 5: Differentiate the penalty
# Differentiate.1*sum(w²) at[1,-2].
# Expected: gradient[.2,-.4].

# Exercise 6: Scale weights deliberately
# Double both weights and compare the new penalties with the original values.
# Expected: L1 doubles to6; squaredL2 quadruples to20.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
