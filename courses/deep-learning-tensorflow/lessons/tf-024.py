"""tf-024: Capstone: a small classifier with honest evaluation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze geometry and groups
# Use training points[-2,-1,1,2], labels[0,0,1,1]; hold out[-3,3].
# Expected: 4 train and2 test records with no shared IDs.

# Exercise 2: Fit training preprocessing
# Calculate training mean and standard deviation, then apply them to both sets.
# Expected: mean0; scale sqrt2.5; test transformed symmetrically.

# Exercise 3: Train within a fixed budget
# Initialize one weight0 and run40 full-batch SGD steps at rate.1 using binary logits
# loss.
# Expected: 40 finite updates and positive final weight.

# Exercise 4: Account for every test row
# Threshold final test logits at0 and compute all four confusion counts.
# Expected: TP1,TN1,FP0,FN0; total2.

# Exercise 5: Compare a baseline
# Predict class0 for every held-out row and report its error count beside the model.
# Expected: baseline1 error; model0 on2 records.

# Exercise 6: Expose a subgroup failure
# Assign test groups negative and positive; flip only the positive prediction and report
# group errors.
# Expected: negative0/1; positive1/1.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
