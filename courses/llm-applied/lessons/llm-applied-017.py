"""llm-applied-017: Quantized frozen bases, adapter gradients and QLoRA limits.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Quantize a fixed matrix
# QuantizeW[[.1, -.9], [1.7, -.2]] withscale1.7/7 andnearest-even rounding.
# Expected: codes[[0, -4], [7, -1]].

# Exercise 2: Pack and unpack real nibbles
# Offset codes by 8, pack adjacent values into two bytes, then unpack.
# Expected: packed bytes[72, 127]; round-trip codes exact.

# Exercise 3: Measure dequantization error
# Reconstructfloat32weights and compareW@x forx[1, -2] with full precision.
# Expected: reference[1.9, 2.1]; finite nonzero approximation error.

# Exercise 4: Train only a small adapter
# Use frozen dequantizedW, rank 1 A/B and10SGD updates towardzero output.
# Expected: adapter loss decreases; packed base bytes unchanged.

# Exercise 5: Account for storage honestly
# Count2 packed bytes plusonefloat32scale, and separately count the
# dequantized2x2float32buffer.
# Expected: packed representation6 bytes; dequantizedbuffer16 bytes; overheadexcluded.

# Exercise 6: State what was not measured
# Write a receipt distinguishing uniform4-bitCPU packing fromNF4, double quantization,
# paged optimizers andGPU memory.
# Expected: all four unimplemented claims explicitlyFalse.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
