"""llm-021: Document splits and contamination controls.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Fingerprint exact text
# Hash two identical snippets and one paraphrase in the same family.
# Expected: identical texts share a hash; paraphrase differs.

# Exercise 2: Assign whole families
# Use documentsa,a2 inF andb inG,c inH; mapF train,G validation,H test.
# Expected: a and a2 both train.

# Exercise 3: Audit all partition pairs
# Construct family sets for train,validation,test and compare pairwise intersections.
# Expected: all three intersections empty.

# Exercise 4: Inject a known leak
# Movea2 into validation and rerun the family intersection.
# Expected: train/validation intersectionF.

# Exercise 5: Preserve the manifest identity
# Hash canonical manifest JSON before and after computing an evaluation summary.
# Expected: hash unchanged.

# Exercise 6: Distinguish normalization policy
# Compare raw hashes for red square and red square followed by a space; compare hashes
# after explicit stripping.
# Expected: raw hashes differ; stripped hashes match.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
