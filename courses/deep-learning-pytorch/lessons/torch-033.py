"""torch-033: Inference mode, model contracts and bounded batching.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a valid batch
# Use float32 CPU rows1, 2 and3, 4.
# Expected: outputs0, 2 with shape(2, ).

# Exercise 2: Check per-record batching parity
# Predict each row alone and concatenate.
# Expected: same values as batch prediction.

# Exercise 3: Reject empty and oversized batches
# Pass shapes0 x2 and5 x2.
# Expected: ValueError naming batch limit.

# Exercise 4: Reject shape and dtype ambiguity
# Pass a vector, a3-feature matrix and an int64 matrix.
# Expected: shape ValueErrors and dtype TypeError.

# Exercise 5: Reject nonfinite values
# Pass aN aN feature and inspect the failure.
# Expected: ValueError for finite-value contract.

# Exercise 6: Preserve caller data
# Mutate the returned output and compare the original input.
# Expected: input unchanged.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
