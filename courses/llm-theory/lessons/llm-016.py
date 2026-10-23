"""llm-016: A tiny causal transformer from explicit parts.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Build a bounded decoder
# Set seed 7, build the default decoder, count every trainable scalar and compare with the
# component ledger.
# Expected: Exactly 10,464 trainable scalars, below the 50,000 teaching bound.

# Exercise 2: Trace output axes
# Run the integer IDs [[2,5,7,3]] and trace the output shape and dtype.
# Expected: Finite float32 logits with shape [1,4,16].

# Exercise 3: Recompute prefixes
# Recompute prefixes of lengths 1 through 4 independently with the same initialized
# weights.
# Expected: Every prefix matches the corresponding full-sequence early logits within 1e-6.

# Exercise 4: Perturb only future tokens
# Replace only positions 2 and 3 with IDs 8 and 9 and compare the first two logits.
# Expected: The first two score vectors remain unchanged within 1e-6.

# Exercise 5: Inspect head shapes
# Run without disabling autograd and inspect the returned K/V cache shapes, detachment and
# data-byte count.
# Expected: Logits remain connected; each cache is detached float32 [1,2,4,16]; combined cache data occupies 1,024 bytes.

# Exercise 6: Reject invalid token IDs
# Reject out-of-range IDs, wrong dtype, empty/excessive context and invalid head/width
# configurations.
# Expected: Every invalid contract raises ValueError before a misleading reshape or embedding computation.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
