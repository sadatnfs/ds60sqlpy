"""torch-022: Attention, transformer masks and information boundaries.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Mix new values causally
# Use zero 3-by-2 queries and keys with values [4, 0], [0, 4], [1, 1] and a causal allowed
# mask.
# Expected: outputs [4, 0], [2, 2] and [5/3, 5/3].

# Exercise 2: Predict a bidirectional change
# Allow every position (an all-True mask) and change only the third value to [10, 10].
# Expected: every row becomes [14/3, 14/3]; without a causal mask the change reaches all rows.

# Exercise 3: Compute one nonuniform weight
# Use queries, keys and values equal to the 2-by-2 identity with a causal mask.
# Expected: row 0 is [1, 0]; row 1 is [1-p, p] with \(p=\sigma(1/\sqrt{2})\), about 0.6698.

# Exercise 4: Reject an all-masked row
# Set the second allowed row to False.
# Expected: ValueError before the attention call.

# Exercise 5: Translate mask polarity explicitly
# Invert the allowed matrix to obtain a forbidden mask for APIs using True as blocked.
# Expected: first forbidden row False, True, True.

# Exercise 6: Keep inference dropout disabled
# Repeat functional attention with dropout_p=0 and compare exact outputs.
# Expected: repeated evaluation matches.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
