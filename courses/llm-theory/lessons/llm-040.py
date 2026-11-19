"""llm-040: A statistical evaluation and reliability argument.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Group a second fixture
# Use families A, B, B, C with paired differences [2, -1, 0, 1]; compute family means, the
# row mean and the equal-family mean.
# Expected: family means A 2, B -0.5, C 1; row mean 0.5; equal-family mean 5/6.

# Exercise 2: Predict bootstrap support
# Draw 2000 resamples of three family means with replacement using seed 3 and predict the
# range and number of distinct estimates.
# Expected: every estimate lies in [-0.5, 2]; at most 10 distinct means occur.

# Exercise 3: Expose row-weighting dependence
# Repeat q1 ten times and compare row mean with unchanged family means.
# Expected: row mean changes; family mean remains 0.

# Exercise 4: Report selective accuracy
# Of 4 questions, answer 2 correctly and abstain on 2. Compute coverage and answered
# accuracy.
# Expected: coverage 0.5; answered accuracy 1; total correct answers 2.

# Exercise 5: Audit decision chronology
# Record prompt selection on validation followed by final-test assessment; flag a test-
# driven prompt change.
# Expected: test-driven selection is invalid for a fresh final claim.

# Exercise 6: Combine gates with uncertainty
# Require no severe failures and adequate family coverage; evaluate a report with one
# severe failure.
# Expected: decision no-go regardless of favorable average.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
