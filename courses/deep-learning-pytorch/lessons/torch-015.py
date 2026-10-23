"""torch-015: Dataset, DataLoader, collation and reproducible sampling.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Inspect retained batches
# Load five paired ID/value records with batch size 2 and no shuffle.
# Expected: sizes 2, 2, 1 and IDs 0..4 exactly once.

# Exercise 2: Make dropping explicit
# Set drop_last True on the same fixture.
# Expected: two batches; ID 4 omitted.

# Exercise 3: Reproduce shuffle with a local generator
# Construct two loaders with fresh generators both seeded 7.
# Expected: same permutation; all five IDs retained.

# Exercise 4: Collate variable-length sequences
# Pad sequences[2, 3] and[4] with zero while keeping lengths.
# Expected: batch[[2, 3], [4, 0]] and lengths 2, 1.

# Exercise 5: Preserve pairing after shuffle
# Load values=2*IDs with shuffling and check each batch.
# Expected: every target equals twice its ID.

# Exercise 6: Reject invalid sequence records
# Pass an empty sequence and floating, Boolean, negative or overflowing token IDs to the
# collator.
# Expected: ValueError before padding; token IDs must be nonnegative int64 integers.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
