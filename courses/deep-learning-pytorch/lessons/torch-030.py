"""torch-030: Distributed gradients and accumulation semantics on CPU.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Weight unequal shard means
# Combine means 2, 6 with counts 1, 3.
# Expected: global mean 5; unweighted shard mean 4.

# Exercise 2: Reconstruct an example mean
# Split gradients 2, 4, 6, 8 into one and three elements and recombine sums/counts.
# Expected: global mean 5.

# Exercise 3: Accumulate one full-batch gradient
# At w=0, usex 1..4, y2x, accumulate squared-loss sums forshards 1 and 3, and divide by 4.
# Expected: gradient-30, matching full-batch mean.

# Exercise 4: Apply one accumulated update
# Take SGD.01 after the global gradient is formed.
# Expected: new weight.3.

# Exercise 5: Contrast separate microbatch updates
# Reset w0and step after each shard mean instead.
# Expected: endpoint differs from.3.

# Exercise 6: Represent empty-shard contributions
# Combine an empty shard and the four real gradients using sums and counts.
# Expected: empty shard contributes 0; global mean 5.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
