"""tf-019: Convolution as a local, shared computation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute local differences
# Apply kernel[[1,0],[0,-1]] to the image1..9 arranged3x3.
# Expected: all four outputs-4.

# Exercise 2: Rotate the kernel
# Reverse both spatial axes and repeat the calculation.
# Expected: all outputs+4.

# Exercise 3: Count output positions
# Compare VALID stride1 and stride2.
# Expected: shapes(1,2,2,1) and(1,1,1,1).

# Exercise 4: Trace one pixel influence
# Add10 to the top-left image pixel and inspect which output changes.
# Expected: only output[0,0] increases10.

# Exercise 5: Count shared parameters
# Construct a bias-free Conv2D layer with2 filters of size2x2 on one input channel.
# Expected: 8 trainable scalars regardless of image height.

# Exercise 6: Add a constant image offset
# Add100 to every pixel and compare outputs under the zero-sum kernel.
# Expected: output unchanged.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
