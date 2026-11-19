"""llm-024: KV caches and incremental equivalence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute a full-prefix oracle
# Initialize the seed-7 decoder and evaluate IDs 2, 5, 7, 3 at once.
# Expected: logits shape (1, 4, 16).

# Exercise 2: Run one token at a time
# Carry returned K/V through four one-token calls and concatenate logits.
# Expected: incremental logits match full within 1e-6.

# Exercise 3: Inspect cache growth
# Check final cache token count and per-head width.
# Expected: cache shape (1, 2, 4, 16).

# Exercise 4: Bind ownership
# Associate the cache with request A and model v1; reject request B.
# Expected: ValueError for foreign request.

# Exercise 5: Start a fresh request empty
# Run token 2 with no cache and compare with the first full-prefix position.
# Expected: logits match the original first position.

# Exercise 6: Invalidate after a model change
# Attempt to use the v1-owned cache with version v2.
# Expected: ValueError for stale version.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
