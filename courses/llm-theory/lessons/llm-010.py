"""llm-010: Position, order and tokenwise normalization.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Permute content-only attention
# Use Q=K=[[1,0],[0,1],[1,1]] and V=[[1,2],[3,4],[5,6]]. Reorder all three by [2,0,1] and
# compare outputs.
# Expected: attention weights move with key identities; output follows the same row reorder; the first original output is [3,4].

# Exercise 2: Normalize each token
# Normalize [[1,3],[10,20]] across each row, then replace only the second row with
# [1000,2000].
# Expected: the first normalized row remains [-1,1]/sqrt(1+1e-5), approximately [-0.999995,0.999995].

# Exercise 3: Expose sequence-wide leakage
# Center each feature across the two token rows, then change the future row from [10,20]
# to [1000,2000].
# Expected: the first centered row changes from [-4.5,-8.5] to [-499.5,-998.5].

# Exercise 4: Attach fixed positions
# Add E=[[0,0],[1,0],[0,2]] to query/key content, then reorder content while keeping E
# attached to the original row positions.
# Expected: fixed-position outputs do not follow a pure content permutation; jointly reordering E restores the relabelling identity.

# Exercise 5: Check feature centering and causal prefixes
# Check tokenwise means, then compare causal attention over normalized full input with
# recomputed prefixes.
# Expected: row means are approximately zero and every causal prefix matches; fixed-mask content permutation need not match.

# Exercise 6: Handle constant tokens and invalid normalization
# Normalize [5,5], then reject an empty feature axis, zero epsilon and an all-forbidden
# attention row.
# Expected: constant token becomes finite [0,0]; each invalid contract raises ValueError.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
