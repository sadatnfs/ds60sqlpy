"""llm-applied-017: Quantized frozen bases, adapter gradients and QLoRA limits.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Quantize a fixed matrix
# Quantize W [[.1, -.9], [1.7, -.2]] with scale 1.7/7 and nearest-even rounding.
# Expected: codes [[0, -4], [7, -1]].

# Exercise 2: Pack and unpack real nibbles
# Offset codes by 8, pack adjacent values into two bytes, then unpack.
# Expected: packed bytes [72, 127]; round-trip codes exact.

# Exercise 3: Measure dequantization error
# Reconstruct float32 weights and compare W@x for x [1, -2] with full precision.
# Expected: reference [1.9, 2.1]; finite nonzero approximation error.

# Exercise 4: Train only a small adapter
# Use frozen dequantized W, rank 1 A/B and 10 SGD updates toward zero output.
# Expected: adapter loss decreases; packed base bytes unchanged.

# Exercise 5: Account for storage honestly
# Count 2 packed bytes plus one float32 scale, and separately count the
# dequantized 2x2 float32 buffer.
# Expected: packed representation 6 bytes; dequantized buffer 16 bytes; overhead excluded.

# Exercise 6: State what was not measured
# Write a receipt distinguishing uniform 4-bit CPU packing from NF4, double quantization,
# paged optimizers and GPU memory.
# Expected: all four unimplemented claims explicitly False.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
