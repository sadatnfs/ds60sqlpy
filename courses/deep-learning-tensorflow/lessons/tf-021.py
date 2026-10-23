"""tf-021: Sequences, embeddings and padding.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Mark valid positions
# Use token IDs[2,3,0] with zero declared padding.
# Expected: mask[True,True,False], count2.

# Exercise 2: Normalize masked losses
# Use token losses[log2,log2,100] and exclude the padding position.
# Expected: masked meanlog2; padding loss100 has no effect.

# Exercise 3: Check embedding axes
# Lookup IDs[2,3,0] in a fixed4x2 table.
# Expected: output shape(3,2); first row[2,2].

# Exercise 4: Append padding
# Add two padding IDs and arbitrary corresponding losses, then recalculate the masked
# mean.
# Expected: mean unchanged atlog2.

# Exercise 5: Select the last valid state
# For token states[[2,2],[3,-1],[99,99]], select the final valid position.
# Expected: state[3,-1], not padding state[99,99].

# Exercise 6: Refuse an empty denominator
# Write a masked-average helper and test an all-padding mask.
# Expected: ValueError for zero valid positions.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
