"""torch-035: Paired model comparisons and uncertainty.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align predictions by ID
# Use truth a0, b1, c2 with A0, 2, 2 andB1, 2, 3 in different dictionary order.
# Expected: paired squared-loss differences-1, 0, -1.

# Exercise 2: Interpret the average contrast
# Average the three paired differences.
# Expected: mean-2/3, favoring A on this loss fixture.

# Exercise 3: Resample pairs reproducibly
# Draw1000 three-index bootstrap samples with local Generator seed 7.
# Expected: 1000 finite estimates within-1..0.

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
