"""llm-applied-013: Paired reliability studies and family-aware uncertainty.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align paired errors
# Use system A errors q1=0, q2=0, q3=1 and B q1=1, q2=1, q3=0.
# Expected: differences [-1, -1, 1] by sorted ID.

# Exercise 2: Aggregate by family
# Assign q1, q2 to family F and q3 to G; compare row mean with family mean.
# Expected: row mean -1/3; family mean 0.

# Exercise 3: Resample paired families
# Draw 2000 bootstrap samples of the two family differences with seed 17.
# Expected: all estimates are -1, 0 or 1; repeatable with same seed.

# Exercise 4: Report coverage and answered accuracy
# For 10 questions, answer 6 with 5 correct and abstain on 4.
# Expected: coverage 0.6; answered accuracy 5/6; overall correct answers 5.

# Exercise 5: Block a severe boundary failure
# Combine a favorable mean comparison with one access leak and apply a zero-access-leak
# gate.
# Expected: release decision False.

# Exercise 6: Keep final tests out of selection
# Record retriever selection on validation and final scoring on test; flag a test-based
# parameter change.
# Expected: test-based selection rejected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
