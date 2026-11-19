"""tf-034: Robustness, privacy and model evidence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count errors for three groups
# Use rows (ID, group, truth, prediction): a A 1 1, b A 0 1, c B 1 1, d B 0 0, e C 1 0, f
# C 0 1, g C 1 1.
# Expected: group A 1/2, group B 0/2, group C 2/3 errors.

# Exercise 2: Deduplicate before reporting
# Append three more copies of row g, then compare group C counts by row and by unique ID.
# Expected: C has 6 rows but 3 unique IDs; the row-level error rate 2/6 understates the 2/3 rate by ID.

# Exercise 3: Evaluate fixed perturbations
# Use f(x)=x>=0 with base 1 and perturbations -0.1, -0.9, -1.1.
# Expected: first two retain class 1; final perturbation changes to 0.

# Exercise 4: Keep severities separate
# Record one severe failure and nine minor passes; count severe failures independently of
# total pass rate.
# Expected: 90 percent passes and 1 severe failure.

# Exercise 5: Write bounded claims
# Create a model card naming the three unique units and untested conditions.
# Expected: card includes count 3 and an untested future-population condition.

# Exercise 6: Reject an empty group rate
# Compute a rate only when its group has observations.
# Expected: empty group produces None, not 0.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
