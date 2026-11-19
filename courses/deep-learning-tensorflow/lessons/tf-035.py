"""tf-035: Comparing models with uncertainty.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align a fourth record
# Use truth a=0, b=1, c=2, d=4, model A predictions d 5, a 0, b 2, c 2 and model B
# predictions b 1, d 4, c 3, a 1. Compute paired squared-error differences by ID.
# Expected: paired differences [-1, 1, -1, 1]; mean 0, so neither model has lower MSE on this fixture.

# Exercise 2: Expose positional pairing
# Pair the original truth, model A and model B dictionaries by insertion order instead of
# ID and compare with the identity-aligned differences.
# Expected: positional differences [-9, 1, 0] instead of [-1, 0, -1].

# Exercise 3: Resample paired units
# Draw 1000 bootstrap index rows with seed 7 and average each selected difference vector.
# Expected: 1000 finite estimates within [-1, 0].

# Exercise 4: Reproduce the resampling
# Repeat with a fresh seed 7 generator and compare the entire estimate vector.
# Expected: exact same estimates.

# Exercise 5: Refuse mismatched IDs
# Remove prediction c from one model and check alignment before computing differences.
# Expected: key-set mismatch detected.

# Exercise 6: Keep selection and final evaluation separate
# Record configuration choice on validation and a single frozen-test assessment; reject a
# later test-driven retune.
# Expected: selection partition validation; final-test tuning prohibited.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
