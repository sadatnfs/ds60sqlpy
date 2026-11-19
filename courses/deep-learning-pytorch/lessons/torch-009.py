"""torch-009: Batches, zero_grad and repeated updates.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Partition with batch size 4
# Partition IDs 1..10 into batches of 4 without dropping the tail.
# Expected: batch sizes 4, 4, 2; the last batch is [9, 10].

# Exercise 2: Count updates with a dropped tail
# With 10 records, batch size 4 and the short tail dropped, count optimizer steps per
# epoch and over 3 epochs.
# Expected: 2 steps per epoch and 6 in total; records 9 and 10 never contribute in unshuffled order.

# Exercise 3: Trace two single-record updates
# Train w from 0 on x = 1, 2 with y = 2x, batch size 1 and learning rate 0.1, clearing
# gradients before each step.
# Expected: weights 0.4 then 1.68.

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
