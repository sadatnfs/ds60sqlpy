"""tf-010: A split is part of the experiment.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Partition accounts
# Use account IDs A,A,B,B,C,C,D,D with values1,3,5,7,20,22,30,32; train on A,B.
# Expected: train mean4 and validation IDs C,D.

# Exercise 2: Expose global fitting
# Change the last validation value to3200 and compare train-only and global means.
# Expected: training mean stays4; global mean changes.

# Exercise 3: Find crossing groups
# Assign alternating rows to train and validation and inspect intersections.
# Expected: A,B,C,D all cross the split.

# Exercise 4: Apply frozen centering
# Center both partitions with training mean4 and compare validation centered values.
# Expected: validation values16,18,26,28.

# Exercise 5: Freeze selection identity
# Hash sorted training IDs before and after calculating validation errors.
# Expected: The selection hash is unchanged.

# Exercise 6: Transfer to unseen accounts
# Add account E with value1000 only to evaluation; specify whether its normalization can
# update the training mean.
# Expected: transformed value996; fitted mean remains4.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
