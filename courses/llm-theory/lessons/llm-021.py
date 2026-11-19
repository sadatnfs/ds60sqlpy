"""llm-021: Document splits and contamination controls.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Assign a second family policy
# Use documents p, p2, p3 in family J, q in K and r in L; map J to test, K to train and L
# to validation.
# Expected: p, p2 and p3 all test; one training document q; r in validation.

# Exercise 2: Predict the effect of key order
# Serialize the same two-entry manifest with keys in opposite orders, with and without
# sort_keys=True, and compare SHA-256 hashes.
# Expected: raw JSON hashes differ when only key order changes; sort_keys=True makes them equal.

# Exercise 3: Audit all partition pairs
# Construct family sets for train, validation, test and compare pairwise intersections.
# Expected: all three intersections empty.

# Exercise 4: Inject a known leak
# Move a2 into validation and rerun the family intersection.
# Expected: train/validation intersection F.

# Exercise 5: Preserve the manifest identity
# Hash canonical manifest JSON before and after computing an evaluation summary.
# Expected: hash unchanged.

# Exercise 6: Distinguish normalization policy
# Compare raw hashes for red square and red square followed by a space; compare hashes
# after explicit stripping.
# Expected: raw hashes differ; stripped hashes match.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
