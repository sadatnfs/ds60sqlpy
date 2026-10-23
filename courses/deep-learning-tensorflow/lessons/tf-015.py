"""tf-015: A reproducible tf.data pipeline.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Observe batches
# Build a dataset from IDs0..4 and values1..5, then batch by2.
# Expected: batch sizes[2,2,1].

# Exercise 2: Apply training statistics
# Use values1,2,3 to fit mean2, then transform all five values without refitting.
# Expected: centered values[-1,0,1,2,3].

# Exercise 3: Retain IDs through mapping
# Reassemble the IDs after centering, batching and prefetch1.
# Expected: IDs0,1,2,3,4 in order.

# Exercise 4: Compare explicit dropping
# Use drop_remainder=True and report which record disappears.
# Expected: sizes[2,2]; ID4 absent.

# Exercise 5: Recreate a deterministic traversal
# Construct the same literal dataset twice and compare complete ordered values.
# Expected: both traversals equal the original five pairs.

# Exercise 6: Check paired transformation
# Scale values by2 and preserve IDs, then verify the value relation2*(ID+1).
# Expected: all five pairs satisfy the relation.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
