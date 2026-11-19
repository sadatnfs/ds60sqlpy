"""torch-035: Paired model comparisons and uncertainty.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align a new pair of models
# Use truth x=1, y=2 with model A predictions x=1, y=4 and model B predictions y=2, x=0 in
# different dictionary order.
# Expected: paired squared-loss differences A minus B: [-1, 4].

# Exercise 2: Interpret the new mean contrast
# Average the two paired differences and state which model the fixture favors.
# Expected: mean 1.5, favoring model B on this loss.

# Exercise 3: Bound the new bootstrap means
# Draw 500 two-index bootstrap samples with Generator seed 11 and inspect the possible
# means.
# Expected: every mean is -1, 1.5 or 4.

# Exercise 4: Replay the local random stream
# Create a new Generator with seed 7 and compare the index matrix.
# Expected: exact match.

# Exercise 5: Reject missing assessment identities
# Remove c from one prediction dictionary and check the keyset.
# Expected: mismatch detected before comparison.

# Exercise 6: Preserve a final-test boundary
# Record configuration choice on validation and assessment on test; flag a test-driven new
# choice.
# Expected: test selection violates the declared boundary.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
