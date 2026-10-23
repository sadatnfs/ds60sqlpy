"""llm-013: A leakage audit before a model score.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct next-token pairs
# Shift IDs[2,5,7,3] into input and label arrays.
# Expected: inputs[2,5,7],labels[5,7,3].

# Exercise 2: Expose identity labels
# Compare copied-input labels with the proper shifted targets.
# Expected: all three copied labels differ from the target fixture.

# Exercise 3: Detect exact duplicates
# Hash texts alpha beta and an identical copy placed in another split.
# Expected: same SHA256 despite different filenames.

# Exercise 4: Detect family leakage
# Assign documentsa andb to familyF across train and validation.
# Expected: family intersection containsF.

# Exercise 5: Freeze a vocabulary
# Fit a vocabulary from training words alpha,beta and encode validation-only gamma without
# adding it.
# Expected: vocabulary remains alpha,beta; gamma is unknown.

# Exercise 6: Count active targets
# Count targets across documents of lengths4 and2 without creating a transition between
# documents.
# Expected: 3+1=4 targets, not5.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
