"""llm-034: Precision and quantization error budgets.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Quantize a second matrix
# Quantize W[[0.5, -1.2], [0.25, 2.0]] with one shared scale, the maximum absolute value
# divided by 127, and nearest-even rounding.
# Expected: scale 2/127; integer array [[32, -76], [16, 127]].

# Exercise 2: Predict the reconstruction error
# Dequantize the new integers and predict the largest absolute weight error and the bound
# it must respect.
# Expected: largest error 0.5/127, about 0.0039, within the half-step bound 1/127.

# Exercise 3: Measure output error
# Dequantize the shared-scale matrix and compare its output with the reference.
# Expected: finite maximum absolute output error below 0.02.

# Exercise 4: Use per-row scales
# Quantize each row using its own maximum absolute value.
# Expected: row scales 0.9/127 and 1.7/127; row 0 integers [14, -127].

# Exercise 5: Account for storage metadata
# Count 4 int8 weights plus one float32 scale versus two float32 row scales.
# Expected: 8 bytes per-tensor; 12 bytes per-row; excluding overhead.

# Exercise 6: Expose clipping and tie policy
# Quantize values exceeding a scale 1 range and inspect nearest-even rounding of 0.5, 1.5,
# 2.5.
# Expected: one saturation for 128; ties round 0, 2, 2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
