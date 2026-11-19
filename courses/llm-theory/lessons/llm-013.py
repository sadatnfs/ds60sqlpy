"""llm-013: A leakage audit before a model score.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Shift a batch of two sequences
# Shift IDs [[4, 1, 6, 2, 9], [3, 3, 8, 0, 5]] along the time axis into inputs and labels.
# Expected: inputs and labels both shape (2, 4); labels [[1, 6, 2, 9], [3, 8, 0, 5]].

# Exercise 2: Predict a partly hidden label bug
# For the second sequence, compare copied-input labels with the shifted targets and
# predict how many positions agree.
# Expected: copied labels agree once (the repeated 3) and differ at the other 3 positions.

# Exercise 3: Detect exact duplicates
# Hash texts alpha beta and an identical copy placed in another split.
# Expected: same SHA256 despite different filenames.

# Exercise 4: Detect family leakage
# Assign documents a and b to family F across train and validation.
# Expected: family intersection contains F.

# Exercise 5: Freeze a vocabulary
# Fit a vocabulary from training words alpha, beta and encode validation-only gamma
# without adding it.
# Expected: vocabulary remains alpha, beta; gamma is unknown.

# Exercise 6: Count active targets
# Count targets across documents of lengths 4 and 2 without creating a transition between
# documents.
# Expected: 3+1=4 targets, not 5.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
