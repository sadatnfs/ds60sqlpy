"""llm-017: Shifted batches, padding and token loss.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Shift the sequence
# Use IDs [2, 5, 7, 3] and create three input-target pairs.
# Expected: inputs 2, 5, 7 and targets 5, 7, 3.

# Exercise 2: Score uniform logits
# Use zero logits with vocabulary 8 for the three targets.
# Expected: mean loss \(\log 8\) and count 3.

# Exercise 3: Append ignored targets
# Add two labels of -100 and corresponding zero-logit positions.
# Expected: mean loss unchanged; active count 3.

# Exercise 4: Expose the wrong denominator
# Compute summed active loss and divide by padded length 5 instead of active count 3.
# Expected: wrong loss \(3\log 8/5\), below the correct loss.

# Exercise 5: Check gradient masking
# Differentiate summed loss and inspect gradient rows at ignored positions.
# Expected: ignored-position gradients exactly zero.

# Exercise 6: Reject all-padding batches
# Check active count before a mean loss on targets [-100, -100].
# Expected: zero active count triggers an explicit failure policy.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
