"""torch-021: Embeddings, padded sequences and recurrent models.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Look up a short sequence
# With the same 4-by-2 table and padding_idx=0, look up IDs [[1, 0, 0]] and build the
# validity mask.
# Expected: values [[1, 0], [0, 0], [0, 0]]; mask [[True, False, False]].

# Exercise 2: Count gradients for repeated IDs
# Look up IDs [[2, 2, 3]] in that embedding, sum the outputs and backpropagate.
# Expected: row 2 gradient [2, 2]; row 3 [1, 1]; rows 0 and 1 zero.

# Exercise 3: Pack a batch with two lengths
# Run a GRU(2, 2) whose parameters are all 0.1 on two padded sequences of lengths 2 and 1,
# packed, and compare each final state with its unpadded run.
# Expected: both final states match their unpadded runs within 1e-6.

# Exercise 4: Expose an unmasked recurrent tail
# Run the GRU over all three positions, including the zero padding embedding.
# Expected: final state differs from the valid-prefix state.

# Exercise 5: Average only valid token losses
# Use losses log 2, log 2, 100 with the valid mask.
# Expected: mean log 2, unchanged by the padding loss.

# Exercise 6: Reject zero-length recurrent input
# Attempt to pack a sequence with length 0.
# Expected: RuntimeError for invalid length.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
