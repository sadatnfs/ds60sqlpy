"""torch-012: Capstone: an auditable tiny PyTorch regressor.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Create the three-feature fixture
# Use rows zero, e1, e2, e3, [1, 1, 1], [2, 1, 1] and target2 a-b+c.
# Expected: targets0, 2, -1, 1, 2, 4.

# Exercise 2: Measure the training-mean baseline
# Fit the constant from training targets and score the two holdout rows.
# Expected: mean.5; holdout MSE7.25.

# Exercise 3: Train a bounded linear model
# Initialize a bias-free3-to-1 Linear layer at zero and run100 SGD.1 updates.
# Expected: 100 finite updates; training loss decreases.

# Exercise 4: Open the holdout after fitting
# Calculate final training and holdout MSE without updates.
# Expected: finite errors; holdout error below7.25 on this fixture.

# Exercise 5: Retain an independent pilot oracle
# Calculate the scalar first update directly from NumPy without using the module.
# Expected: w28/15 and loss56/675.

# Exercise 6: Write the bounded evidence report
# Record split IDs, 100 steps, errors and the two-row limitation.
# Expected: disjoint IDs; holdout count 2; explicit limited scope.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
