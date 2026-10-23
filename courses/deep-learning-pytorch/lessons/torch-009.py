"""torch-009: Batches, zero_grad and repeated updates.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count batches and updates
# Partition IDs 1..6 into batches of 2.
# Expected: three batches[[1, 2], [3, 4], [5, 6]].

# Exercise 2: Retain a short tail
# Partition five IDs with batch size 2.
# Expected: batch sizes 2, 2, 1.

# Exercise 3: Run three independent updates
# Train x1..6, y2x, w0 with batch size 2, rate.01, clearing gradients each batch.
# Expected: three finite distinct weights.

# Exercise 4: Expose accidental accumulation
# Repeat the loop without zero_grad and compare its final weight with the correct run.
# Expected: different endpoint.

# Exercise 5: Shuffle paired records together
# Use permutation 5, 0, 4, 1, 3, 2 for both x and y.
# Expected: every shuffled target equals twice its input.

# Exercise 6: Aggregate unequal batch means
# Combine mean loss 2 over 2 examples and mean loss 8 over 1 example.
# Expected: epoch mean 4, not 5.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
