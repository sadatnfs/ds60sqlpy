"""tf-033: Inference contracts and bounded batching.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a valid batch
# Predict for float32 rows[1,2],[3,4].
# Expected: outputs0,2 with shape(2,).

# Exercise 2: Compare batch independence
# Predict each row independently and compare concatenated outputs with the batch result.
# Expected: exact equality for this fixed linear fixture.

# Exercise 3: Reject empty and oversized batches
# Pass shapes(0,2) and(5,2).
# Expected: ValueError with batch in the message.

# Exercise 4: Reject wrong feature structure
# Pass a vector[1,2] and a matrix with three columns.
# Expected: ValueError with shape in the message.

# Exercise 5: Reject nonfinite values and wrong dtype
# Pass a NaN row and an int64 row under the explicit float32 policy.
# Expected: ValueError for nonfinite; TypeError for dtype.

# Exercise 6: Preserve the input
# Snapshot a valid batch, predict and mutate the returned result; compare the original
# input.
# Expected: input remains byte-identical.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
