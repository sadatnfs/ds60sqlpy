"""torch-019: Convolutions, channel layouts and shared computation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute the fixed spatial filter
# Apply kernel 1, 0; 0, -1 to image 1..9 in 3 x3NCHW layout.
# Expected: output shape 1, 1, 2, 2; all values-4.

# Exercise 2: Rotate the kernel explicitly
# Flip both kernel spatial axes and repeat.
# Expected: all outputs+4.

# Exercise 3: Translate image layout
# Convert NCHW to NHWC with permute and back.
# Expected: exact round trip; NHWC shape 1, 3, 3, 1.

# Exercise 4: Inspect stride output size
# Repeat with stride 2 and padding 0.
# Expected: output shape 1, 1, 1, 1.

# Exercise 5: Trace one pixel influence
# Add 10 to the top-left pixel and compare output delta.
# Expected: only top-left output increases 10.

# Exercise 6: Count shared parameters
# Build a1-input-channel, 2-output-channel, 2x2bias-free Conv2d.
# Expected: 8trainable scalars.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
