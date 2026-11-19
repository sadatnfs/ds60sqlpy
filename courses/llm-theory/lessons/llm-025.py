"""llm-025: Memory and compute without a GPU.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count scores for a larger configuration
# Use batch 2, heads 4 and context 64 with 4-byte score elements.
# Expected: 32768 score elements; 131072 bytes (128 KiB).

# Exercise 2: Predict cache growth with depth and context
# Use 3 layers, 2 heads, width per head 16, 4-byte elements and contexts 48 and 96;
# compare with the growth of the score matrix.
# Expected: 36864 and 73728 cache bytes; the cache doubles while score elements quadruple.

# Exercise 3: Compare element precision
# Calculate cache bytes at context 32 using 2-byte versus 4-byte elements.
# Expected: 4096 versus 8192 bytes.

# Exercise 4: Scale batch size
# Increase batch from 1 to 3 with context 32 and all other cache dimensions fixed.
# Expected: 24576 raw cache bytes.

# Exercise 5: Preserve total width
# Compare 4 heads of width 8 with 2 heads of width 16.
# Expected: equal raw cache bytes for the same context.

# Exercise 6: State exclusions
# Produce an estimate record naming omitted allocations and avoid calling it peak memory.
# Expected: record identifies parameters, temporary tensors, allocator overhead as excluded.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
