"""tf-010: A split is part of the experiment.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Partition a second account fixture
# Use groups E, E, F, F, G, G, H, H with values 2, 4, 6, 8, 10, 12, 40, 44; train on E, F
# and G, then center the held-out rows with the training mean.
# Expected: train mean 7; validation group H; centered values 33 and 37.

# Exercise 2: Predict the effect of a training outlier
# Change the first training value from 2 to 200. Predict the new training mean and the
# centered validation values before running the check.
# Expected: training mean 40; centered H values 0 and 4.

# Exercise 3: Find crossing groups
# Assign alternating rows to train and validation and inspect intersections.
# Expected: A, B, C, D all cross the split.

# Exercise 4: Apply frozen centering
# Center both partitions with training mean 4 and compare validation centered values.
# Expected: validation values 16, 18, 26, 28.

# Exercise 5: Freeze selection identity
# Hash sorted training IDs before and after calculating validation errors.
# Expected: The selection hash is unchanged.

# Exercise 6: Transfer to unseen accounts
# Add account E with value 1000 only to evaluation; specify whether its normalization can
# update the training mean.
# Expected: transformed value 996; fitted mean remains 4.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
