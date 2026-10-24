"""llm-043: Encoder, decoder and encoder-decoder architectures and objectives.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare bidirectional and causal mixtures
# Use zero queries/keys and values[[2, 0], [0, 2], [6, 6]] under all-allowed and causal
# masks.
# Expected: encoder rows all[8/3, 8/3]; decoder rows[2, 0], [1, 1], [8/3, 8/3].

# Exercise 2: Trace rectangular cross-attention
# Use two zero target queries, three zero source keys and the same source values.
# Expected: score/weight shape(2, 3); output shape(2, 2); both outputs[8/3, 8/3].

# Exercise 3: Build shifted decoder targets
# For target IDs[5, 7, 3], prepend BOS1 and form input/label pairs.
# Expected: inputs[1, 5, 7]; labels[5, 7, 3]; diagonal allowed without seeing the target itself.

# Exercise 4: Separate masked-token supervision
# Corrupt source[2, 5, 7] at the middle position with MASK0 and supervise only that
# original token.
# Expected: input[2, 0, 7]; one active label5; bidirectional context remains allowed.

# Exercise 5: Perturb future target values
# Change only the third value vector and compare the first two encoder/decoder outputs.
# Expected: encoder prefix changes; causal decoder prefix stays fixed.

# Exercise 6: Combine source padding with cross-attention
# Mark the third source position as padding for both target queries.
# Expected: both cross outputs[1, 1]; padded source weight0.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
