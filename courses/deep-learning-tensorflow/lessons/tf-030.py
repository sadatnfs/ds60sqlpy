"""tf-030: Distributed gradient semantics on one CPU.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Weight shard means
# Combine means 2, 6 with counts 1, 3 and compare equal shard averaging.
# Expected: global 5; naive 4.

# Exercise 2: Recover a full-batch mean
# Partition gradients [2, 4, 6, 8] into sizes 1 and 3 and reconstruct their mean.
# Expected: both full and reconstructed means 5.

# Exercise 3: Accumulate squared-loss gradients
# At w = 0 use x = [1, 2, 3, 4], y = 2x; compare full-batch gradient with sum-then-divide
# microbatches.
# Expected: gradient -30 for both.

# Exercise 4: Apply exactly one update
# Use rate 0.01 with accumulated global gradient -30.
# Expected: updated weight 0.3.

# Exercise 5: Expose per-batch updates
# Update separately for the two microbatches and compare the final weight with 0.3.
# Expected: endpoint differs from 0.3.

# Exercise 6: Handle an empty shard
# Combine an empty shard and the four real gradients using sums and counts; reject a
# globally empty batch.
# Expected: empty shard contributes 0; total remains 5.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
