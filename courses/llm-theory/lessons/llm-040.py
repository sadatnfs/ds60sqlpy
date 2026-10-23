"""llm-040: A statistical evaluation and reliability argument.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align paired question results
# Use questionsq1,q2 inA andq3 inB; system error differences[-1,-1,1].
# Expected: question mean-1/3;family meansA-1,B1.

# Exercise 2: Resample whole families
# Draw1000 bootstrap samples of the two family differences with seed8.
# Expected: estimates only-1,0,1;mean of original family values0.

# Exercise 3: Expose row-weighting dependence
# Repeatq1 ten times and compare row mean with unchanged family means.
# Expected: row mean changes;family mean remains0.

# Exercise 4: Report selective accuracy
# Of4 questions,answer2 correctly and abstain on2. Compute coverage and answered accuracy.
# Expected: coverage.5;answered accuracy1;total correct answers2.

# Exercise 5: Audit decision chronology
# Record prompt selection onvalidation followed by final-test assessment; flag a test-
# driven prompt change.
# Expected: test-driven selection is invalid for a fresh final claim.

# Exercise 6: Combine gates with uncertainty
# Require no severe failures and adequate family coverage; evaluate a report withone
# severe failure.
# Expected: decisionno-go regardless of favorable average.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
