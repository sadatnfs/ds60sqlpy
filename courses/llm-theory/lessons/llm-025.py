"""llm-025: Memory and compute without a GPU.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count attention scores
# Use batch1,heads2 and contexts16,32.
# Expected: 512 and2048 score elements.

# Exercise 2: Count raw cache bytes
# Use1 layer,2 heads,width per head16,float32 bytes4 and contexts16,32.
# Expected: 4096 and8192 bytes.

# Exercise 3: Compare element precision
# Calculate cache bytes at context32 using2-byte versus4-byte elements.
# Expected: 4096 versus8192 bytes.

# Exercise 4: Scale batch size
# Increase batch from1 to3 with context32 and all other cache dimensions fixed.
# Expected: 24576 raw cache bytes.

# Exercise 5: Preserve total width
# Compare4 heads of width8 with2 heads of width16.
# Expected: equal raw cache bytes for the same context.

# Exercise 6: State exclusions
# Produce an estimate record naming omitted allocations and avoid calling it peak memory.
# Expected: record identifies parameters,temporary tensors,allocator overhead as excluded.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
