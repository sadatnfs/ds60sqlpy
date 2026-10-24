"""llm-applied-013: Paired reliability studies and family-aware uncertainty.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align paired errors
# Use systemA errors q1=0, q2=0, q3=1 andB q1=1, q2=1, q3=0.
# Expected: differences[-1, -1, 1] by sortedID.

# Exercise 2: Aggregate by family
# Assignq1, q2 tofamilyF andq3 toG; compare row mean with family mean.
# Expected: row mean-1/3; family mean0.

# Exercise 3: Resample paired families
# Draw2000 bootstrap samples of the two family differences withseed17.
# Expected: all estimates are-1, 0 or1; repeatable with same seed.

# Exercise 4: Report coverage and answered accuracy
# For10 questions, answer6 with 5 correct and abstain on4.
# Expected: coverage.6; answered accuracy5/6; overall correct answers5.

# Exercise 5: Block a severe boundary failure
# Combine a favorable mean comparison withone access leak and apply a zero-access-leak
# gate.
# Expected: release decisionFalse.

# Exercise 6: Keep final tests out of selection
# Record retriever selection onvalidation and final scoring ontest; flag a test-based
# parameter change.
# Expected: test-based selection rejected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
