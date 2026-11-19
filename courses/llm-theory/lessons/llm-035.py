"""llm-035: Inference scheduling and cache isolation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Define unequal requests
# Use request A tokens 2, 5, 7 and B tokens 1, 3 with separate cache keys.
# Expected: lengths 3 and 2; distinct keys.

# Exercise 2: Interleave bounded work
# Process A0, B0, A1, B1, A2 with independent caches.
# Expected: cache lengths A3, B2.

# Exercise 3: Compare independent inference
# Run each complete request without a cache and compare its concatenated incremental
# logits.
# Expected: both requests match within 1e-6.

# Exercise 4: Invalidate a tokenizer change
# Look up A under tokenizer v2 rather than v1.
# Expected: no cached state found.

# Exercise 5: Invalidate a model change
# Look up A under model v2 with the same tokenizer.
# Expected: no cached state found.

# Exercise 6: Respect independent caps
# Set caps A3, B2 and verify scheduled counts; reject one extra B token.
# Expected: A and B at their own caps; B cannot advance.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
