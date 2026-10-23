"""llm-016: A tiny causal transformer from explicit parts.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Build a bounded decoder
# Set seed7, construct the decoder and count trainable scalar parameters.
# Expected: parameter count below50000.

# Exercise 2: Trace output axes
# Run input IDs[[2,5,7,3]] and inspect logits.
# Expected: shape(1,4,16), all finite.

# Exercise 3: Recompute prefixes
# Run prefix lengths1..4 independently in evaluation mode.
# Expected: prefix logits match full early logits within1e-6.

# Exercise 4: Perturb only future tokens
# Replace positions2,3 with8,9 and compare the first two outputs.
# Expected: first two logits unchanged within1e-6.

# Exercise 5: Inspect head shapes
# Read the returned K/V state after four tokens.
# Expected: each cache tensor shape(1,2,4,16).

# Exercise 6: Reject invalid token IDs
# Pass vocabulary ID16 and a33-token context.
# Expected: both raise ValueError.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
