"""llm-032: Low-rank adaptation without a package download.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count adapter parameters
# Use W=I8, A=ones(8, 2)/8, B=zeros(2, 8).
# Expected: adapter 32 parameters versus base64.

# Exercise 2: Check zero initial delta
# Compare x@(W+A@B) with x@W before training.
# Expected: both equal ones(1, 8).

# Exercise 3: Differentiate the first objective
# Use mean squared error to a zero target and inspect both adapter gradients.
# Expected: A gradient zero; B gradient nonzero.

# Exercise 4: Update only the adapter
# Take one SGD(0.1) step over A, B.
# Expected: B changes; W remains exactly equal.

# Exercise 5: Observe the changed function
# Recompute the zero-target squared error after the adapter step.
# Expected: loss decreases for this fixture.

# Exercise 6: Bound the update rank
# Compute the numerical matrix rank of A@B after the step.
# Expected: rank at most 2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
