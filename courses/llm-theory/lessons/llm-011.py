"""llm-011: Multiple heads, residuals and a decoder block.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Split and rejoin
# Split X=[[0,1,2,3],[4,5,6,7]] into two heads, inspect membership, then invert the
# layout.
# Expected: head zero is [[0,1],[4,5]], head one is [[2,3],[6,7]], and rejoining restores X exactly.

# Exercise 2: Calculate a residual
# Add branch 2X to X, then compare with zero and cancelling branches.
# Expected: 2X gives 3X, zero branch gives X, and branch -X gives zero; all retain the same shape.

# Exercise 3: Use a tokenwise nonlinear block
# Apply the explicit identity-weight, bias-minus-two feed-forward branch to two token
# rows.
# Expected: first output [0,0,0,1]; changing the second token does not change the first output.

# Exercise 4: Test actual head mixtures and causal prefixes
# Run the three-token four-feature fixture through two causal heads and compare
# independently recomputed prefixes.
# Expected: head distributions differ as derived, row-one output is [1/(1+a),a/(1+a),1,0.5], and every prefix matches.

# Exercise 5: Reject an indivisible width
# Call the split helper with width 5 and two heads, then with zero heads and an empty
# token axis.
# Expected: each invalid layout raises ValueError before reshape.

# Exercise 6: Detect a wrong rejoin
# Flatten the head-major tensor directly and compare values with the correctly inverted
# transpose.
# Expected: the wrong [2,4] result differs despite matching shape; the inverse operation restores X.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
