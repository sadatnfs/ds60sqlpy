"""torch-034: Robustness, privacy and evidence beyond a score.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count errors for three groups
# Use groups A, B, B, C with truth 0, 1, 1, 0 and predictions 0, 0, 1, 1.
# Expected: A: 0 of 1 wrong; B: 1 of 2; C: 1 of 1.

# Exercise 2: Deduplicate repeated identities
# Use row identities p, q, q, r, r, r and count rows, unique identities and the largest
# repeat.
# Expected: 6 rows, 3 unique identities, largest repeat 3.

# Exercise 3: Trace a new perturbation
# Classify x>=0 at base 0.5 after shifts -0.4, -0.5 and -0.6.
# Expected: labels 1, 1, 0; the shift of -0.5 lands exactly on the boundary.

# Exercise 4: Keep severe failures visible
# Use 9 minor passes and 1 severe failure.
# Expected: overall pass rate 0.9; severe failure count 1.

# Exercise 5: Represent an untested group
# Define a rate helper with count 0.
# Expected: None for untested; 0 for zero errors in one case.

# Exercise 6: Write a bounded card
# Record 3 unique units, synthetic teaching use and untested future conditions.
# Expected: card explicitly has no privacy guarantee.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
