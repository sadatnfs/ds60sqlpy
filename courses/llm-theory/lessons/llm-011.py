"""llm-011: Multiple heads, residuals and a decoder block.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Split and rejoin
# Reshape two width4 rows into2 heads of width2, then invert the layout change.
# Expected: exact round trip and head width2.

# Exercise 2: Calculate a residual
# Apply a branch2*x and add the original input.
# Expected: result3*x with unchanged shape.

# Exercise 3: Use a tokenwise nonlinear block
# Apply max(x-2,0) independently and project with identity.
# Expected: first row[0,0,0,1].

# Exercise 4: Test a prefix
# Recompute the feed-forward branch on only the first row and compare with the full
# result.
# Expected: first-row output unchanged.

# Exercise 5: Reject an indivisible width
# Check width5 with2 heads before reshaping.
# Expected: divisibility check fails.

# Exercise 6: Detect a wrong rejoin
# Flatten the transposed heads without first reversing the transpose.
# Expected: wrong result differs from the original rows.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
