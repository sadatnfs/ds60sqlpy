"""llm-046: MHA, MQA, GQA and blockwise exact attention.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count cache and projection dimensions
# Use batch 1, time 5, 4 query heads, head width 2 and float32, and compare 4, 2 and 1 KV
# heads.
# Expected: raw KV bytes 320, 160, 80; projection weights 256, 192, 160 for model width 8 without biases.

# Exercise 2: Verify grouped heads against an equivalent repeated-head oracle
# Use 4 query heads and 2 KV heads; repeat each KV head twice only in the dense oracle.
# Expected: outputs agree within1e-12; shape(4, 3, 2).

# Exercise 3: Trace online softmax at extreme scores
# Combine scores 1000, 999, 998 and values 1, 3, 5 in blocks of 2.
# Expected: finite output equals a maximum-shifted dense calculation.

# Exercise 4: Compare several block sizes under causal masking
# Use five nonuniform query/key rows and compare block sizes 1, 2, 3, 5 with dense
# attention.
# Expected: all outputs agree within1e-12; largest temporary score block does not exceed the chosen size.

# Exercise 5: Preserve a causal prefix under future changes
# Change only value rows 3 and 4 and compare the first three online outputs.
# Expected: first three rows unchanged.

# Exercise 6: Reject invalid grouping and empty support
# Try 4 query heads with 3 KV heads, and an all-false attention row.
# Expected: both raise ValueError; no output NaNs are accepted.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
