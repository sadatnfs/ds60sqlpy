"""torch-021: Embeddings, padded sequences and recurrent models.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Lookup and mark padding
# Use IDs 2, 3, 0 and a fixed 4 x2table with zero padding row.
# Expected: embedding shape 1, 3, 2; mask True, True, False.

# Exercise 2: Verify padding-row gradient behavior
# Sum embedding outputs and backpropagate.
# Expected: padding row gradient zero; rows 2 and 3nonzero.

# Exercise 3: Compare packed and valid-prefix GRU state
# Use fixed GRU parameters.1 and length 2; compare packed run with the unpadded first two
# embeddings.
# Expected: final states match within 1e-6.

# Exercise 4: Expose an unmasked recurrent tail
# Run GRU overall three positions including zero embedding padding.
# Expected: final state differs from the valid-prefix state.

# Exercise 5: Average only valid token losses
# Use losses log 2, log 2, 100with the valid mask.
# Expected: mean log 2, unchanged by the padding loss.

# Exercise 6: Reject zero-length recurrent input
# Attempt to pack a sequence with length 0.
# Expected: RuntimeError for invalid length.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
