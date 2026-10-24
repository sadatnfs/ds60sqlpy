"""tf-012: Capstone: an auditable tiny regressor.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze six records
# Create the three-feature fixture below, assign IDs0..3 to train and4..5 to holdout, and
# calculate targets.
# Expected: targets[0,2,-1,1,2,4], disjoint IDs.

# Exercise 2: Measure the baseline
# Use the training mean to predict both held-out targets and compute squared error.
# Expected: training mean.5; holdout MSE7.25.

# Exercise 3: Train a bounded model
# Initialize a three-by-one kernel at zero and make exactly100 full-training SGD updates
# at rate.1.
# Expected: 100 updates; finite weights; training error below its initial value.

# Exercise 4: Open the holdout once
# Compute held-out MSE after the fixed100 updates and compare it with the frozen baseline.
# Expected: holdout error below7.25 on the two supplied records.

# Exercise 5: Preserve arithmetic evidence
# Derive a one-feature pilot update from x1,2,3 and target2x at w0,rate.1.
# Expected: weight28/15 and loss56/675.

# Exercise 6: Reject a false conclusion
# Construct a report containing split IDs, errors, step count and limitations; refuse a
# production-quality claim from two holdout rows.
# Expected: report names2 holdout records and makes no population guarantee.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
