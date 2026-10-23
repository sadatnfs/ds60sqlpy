"""llm-034: Precision and quantization error budgets.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute the full-precision reference
# Multiply W[[.1,-.9],[1.7,-.2]] byx[1,-2].
# Expected: output[1.9,2.1].

# Exercise 2: Quantize one shared scale
# Use maxabs1.7 divided by127,nearest-even rounding and signed int8.
# Expected: scale1.7/127;integer array[[7,-67],[127,-15]].

# Exercise 3: Measure output error
# Dequantize the shared-scale matrix and compare its output with the reference.
# Expected: finite maximum absolute output error below.02.

# Exercise 4: Use per-row scales
# Quantize each row using its own maximum absolute value.
# Expected: row scales.9/127 and1.7/127;row0 integers[14,-127].

# Exercise 5: Account for storage metadata
# Count4 int8 weights plusone float32 scale versus two float32 row scales.
# Expected: 8 bytes per-tensor;12 bytes per-row;excluding overhead.

# Exercise 6: Expose clipping and tie policy
# Quantize values exceeding a scale1 range and inspect nearest-even rounding of.5,1.5,2.5.
# Expected: one saturation for128;ties round0,2,2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
