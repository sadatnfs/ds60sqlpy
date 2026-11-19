"""torch-033: Inference mode, model contracts and bounded batching.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a new valid batch
# Predict the float32 rows [0, 1], [2, 0] and [1, 1] with the lesson's weight [2, -1].
# Expected: outputs [-1, 4, 1] with shape (3,).

# Exercise 2: Check the batch boundary
# Predict a batch of four rows of ones, then a batch of five.
# Expected: four rows return shape (4,); five rows raise ValueError.

# Exercise 3: Reject a float64 batch
# Pass the three valid rows converted to float64.
# Expected: TypeError rather than a silent conversion.

# Exercise 4: Reject shape and dtype ambiguity
# Pass a vector, a 3-feature matrix and an int64 matrix.
# Expected: shape ValueErrors and dtype TypeError.

# Exercise 5: Reject nonfinite values
# Pass a NaN feature and inspect the failure.
# Expected: ValueError for finite-value contract.

# Exercise 6: Preserve caller data
# Mutate the returned output and compare the original input.
# Expected: input unchanged.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
