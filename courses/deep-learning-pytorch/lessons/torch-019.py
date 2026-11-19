"""torch-019: Convolutions, channel layouts and shared computation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Apply a summing kernel
# Apply the 2-by-2 kernel of ones to the 3-by-3 image with values 1..9 in NCHW layout.
# Expected: outputs [[12, 16], [24, 28]] in shape (1, 1, 2, 2).

# Exercise 2: Predict the shape with padding
# Repeat the summing kernel with padding=1 and predict the output shape and its top-left
# value.
# Expected: shape (1, 1, 4, 4); top-left value 1.

# Exercise 3: Permute a two-channel image
# Stack the image and its negative as two channels, convert NCHW to NHWC and read the
# channel pair at row 0, column 2.
# Expected: NHWC shape (1, 3, 3, 2); the pair is [3, -3].

# Exercise 4: Inspect stride output size
# Repeat with stride 2 and padding 0.
# Expected: output shape 1, 1, 1, 1.

# Exercise 5: Trace one pixel influence
# Add 10 to the top-left pixel and compare output delta.
# Expected: only top-left output increases 10.

# Exercise 6: Count shared parameters
# Build a bias-free Conv2d with 1 input channel, 2 output channels and a 2-by-2 kernel.
# Expected: 8 trainable scalars.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
