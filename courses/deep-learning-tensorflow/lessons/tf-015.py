"""tf-015: A reproducible tf.data pipeline.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Replay a seeded shuffle
# Shuffle the five records with shuffle(5, seed=7, reshuffle_each_iteration=False).
# Traverse it twice, rebuild the same pipeline from the literal arrays, and compare the ID
# orders.
# Expected: the same ID order on both passes and after rebuilding; IDs 0-4 each appear once; every value is still ID+1.

# Exercise 2: Predict a different batch size
# Predict the batch sizes for batch(3), then the surviving IDs when drop_remainder=True,
# before running the pipeline.
# Expected: sizes [3, 2]; with drop_remainder=True only IDs 0, 1, 2 remain.

# Exercise 3: Retain IDs through mapping
# Reassemble the IDs after centering, batching and prefetch 1.
# Expected: IDs 0, 1, 2, 3, 4 in order.

# Exercise 4: Compare explicit dropping
# Use drop_remainder=True and report which record disappears.
# Expected: sizes [2, 2]; ID 4 absent.

# Exercise 5: Recreate a deterministic traversal
# Construct the same literal dataset twice and compare complete ordered values.
# Expected: both traversals equal the original five pairs.

# Exercise 6: Check paired transformation
# Scale values by 2 and preserve IDs, then verify the value relation 2*(ID+1).
# Expected: all five pairs satisfy the relation.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
