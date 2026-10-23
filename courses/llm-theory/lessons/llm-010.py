"""llm-010: Position, order and tokenwise normalization.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Permute content-only attention
# Use Q=K[[1,0],[0,1],[1,1]],V[[1,2],[3,4],[5,6]]; jointly permute rows2,0,1.
# Expected: permuted output equals original output rows2,0,1.

# Exercise 2: Normalize each token
# Normalize rows[1,3] and[10,20] independently, then alter only the second row.
# Expected: first normalized row unchanged.

# Exercise 3: Expose sequence-wide leakage
# Center each feature across both token rows, then repeat after changing the future row.
# Expected: first centered row changes.

# Exercise 4: Attach fixed positions
# Add position vectors[[0,0],[1,0],[0,2]]; permute content but keep positions fixed.
# Expected: outputs no longer follow a pure token permutation.

# Exercise 5: Check feature centering
# Inspect tokenwise normalized row means for the original fixture.
# Expected: each row mean approximately0.

# Exercise 6: Handle constant tokens
# Normalize[5,5] with epsilon1e-5.
# Expected: finite vector[0,0].

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
