"""tf-014: Multiclass and multilabel are different tasks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Uniform class uncertainty
# Compute sparse cross entropy for target 1 and three zero logits.
# Expected: loss log(3).

# Exercise 2: Independent labels
# Calculate sigmoid probabilities for three zero logits and labels [1, 0, 1].
# Expected: three probabilities 0.5 with total 1.5.

# Exercise 3: Contrast target shapes
# Build sparse targets [2, 0] and multilabel targets [[1, 0, 1], [0, 1, 0]].
# Expected: shapes (2,) and (2, 3).

# Exercise 4: Verify softmax mass
# Apply softmax to [[2, 0, -2]] and compare its sum with sigmoid output.
# Expected: softmax sum 1; sigmoid sum 1.5.

# Exercise 5: Choose the denominator
# Compute binary cross entropy for two three-label rows of zero logits; compare sum with
# entry mean.
# Expected: sum 6 log 2; mean log 2.

# Exercise 6: Reject an impossible class
# Validate a sparse class index before lookup in a three-class vocabulary.
# Expected: index 3 is outside legal indices 0, 1, 2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
