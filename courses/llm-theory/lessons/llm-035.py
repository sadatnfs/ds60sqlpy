"""llm-035: Inference scheduling and cache isolation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Define unequal requests
# Use requestA tokens2,5,7 andB tokens1,3 with separate cache keys.
# Expected: lengths3 and2;distinct keys.

# Exercise 2: Interleave bounded work
# ProcessA0,B0,A1,B1,A2 with independent caches.
# Expected: cache lengthsA3,B2.

# Exercise 3: Compare independent inference
# Run each complete request without a cache and compare its concatenated incremental
# logits.
# Expected: both requests match within1e-6.

# Exercise 4: Invalidate a tokenizer change
# Look upA under tokenizerv2 rather thanv1.
# Expected: no cached state found.

# Exercise 5: Invalidate a model change
# Look upA under modelv2 with the same tokenizer.
# Expected: no cached state found.

# Exercise 6: Respect independent caps
# Set capsA3,B2 and verify scheduled counts; reject one extraB token.
# Expected: A andB at their own caps;B cannot advance.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
