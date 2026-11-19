"""torch-036: Capstone: release a small reproducible PyTorch model.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze a new split
# Assign IDs a, b, c, d to training and e, f to holdout and check that the sets are
# disjoint.
# Expected: 4 training and 2 holdout IDs with no overlap.

# Exercise 2: Predict a ten-step weight
# Train a zero-initialized float64 Linear(1, 1) without bias for 10 SGD steps with
# learning rate 0.01 on x = 1, 2, 3 and y = 2x.
# Expected: weight 2-2*(68/75)**10, about 1.2492, within 1e-12.

# Exercise 3: Hash bytes deterministically
# Compute the SHA-256 of the bytes weights-v2 twice and of weights-v3 once.
# Expected: identical bytes give identical 64-character digests; one changed byte changes the digest.

# Exercise 4: Verify fresh-process prediction parity
# Run the checked loader in a fresh interpreter and compare holdout predictions.
# Expected: predictions match within 1e-12.

# Exercise 5: Make a corrupted artifact fail
# Replace the declared weight hash with 64 zeros and rerun the loader.
# Expected: nonzero child exit and weight hash mismatch diagnostic.

# Exercise 6: Record a bounded decision and cleanup
# Record local parity pass, holdout count 2, previous artifact v1 and production no-go,
# then remove owned files.
# Expected: local checks True; production no-go; directory absent.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
