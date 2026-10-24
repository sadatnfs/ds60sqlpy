"""torch-014: CrossEntropyLoss, multiclass and multilabel contracts.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate uniform multiclass loss
# Use one row of three zero logits and target class 1.
# Expected: cross entropy log 3.

# Exercise 2: Contrast independent binary outputs
# Apply sigmoid to the same three zero logits for a multilabel task.
# Expected: probabilities.5, .5, .5 with sum 1.5.

# Exercise 3: Inspect target shapes and types
# Create class indices 2, 0 and binary rows[1, 0, 1], [0, 1, 0].
# Expected: shapes(2, ) and(2, 3); long versus floating.

# Exercise 4: Check class-axis normalization
# Apply softmax(dim 1) to a2x3matrix.
# Expected: each row sums 1.

# Exercise 5: Name the multilabel denominator
# Compute BCE over two rows and three labels of zero logits.
# Expected: sum 6 log2; mean log 2.

# Exercise 6: Reject an out-of-vocabulary class
# Use class index 3 for a three-class row.
# Expected: IndexError or RuntimeError identifying an invalid target.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
