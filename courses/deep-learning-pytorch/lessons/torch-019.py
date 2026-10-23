"""torch-019: Convolutions, channel layouts and shared computation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute the fixed spatial filter
# Apply kernel1, 0; 0, -1 to image1..9 in3 x3 NCHW layout.
# Expected: output shape1, 1, 2, 2; all values-4.

# Exercise 2: Rotate the kernel explicitly
# Flip both kernel spatial axes and repeat.
# Expected: all outputs+4.

# Exercise 3: Translate image layout
# Convert NCHW to NHWC with permute and back.
# Expected: exact round trip; NHWC shape1, 3, 3, 1.

# Exercise 4: Inspect stride output size
# Repeat with stride2 and padding0.
# Expected: output shape1, 1, 1, 1.

# Exercise 5: Trace one pixel influence
# Add10 to the top-left pixel and compare output delta.
# Expected: only top-left output increases10.

# Exercise 6: Count shared parameters
# Build a1-input-channel, 2-output-channel, 2 x2 bias-free C on v2 d.
# Expected: 8 trainable scalars.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
