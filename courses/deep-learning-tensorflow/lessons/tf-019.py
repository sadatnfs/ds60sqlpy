"""tf-019: Convolution as a local, shared computation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Detect a horizontal difference
# Keep the 1..9 ramp image but use the kernel `[[1, -1], [0, 0]]`, which compares each
# pixel with its right neighbor. Predict the four VALID outputs before running it.
# Expected: all four outputs -1.

# Exercise 2: Predict SAME padding
# Repeat the diagonal-kernel calculation with `padding='SAME'`. Predict the output shape
# and the nine values, remembering that TensorFlow pads a 2x2 kernel with zeros on the
# bottom and right.
# Expected: shape (1, 3, 3, 1); values [[-4, -4, 3], [-4, -4, 6], [7, 8, 9]].

# Exercise 3: Count output positions
# Compare VALID stride 1 and stride 2.
# Expected: shapes (1, 2, 2, 1) and (1, 1, 1, 1).

# Exercise 4: Trace one pixel influence
# Add 10 to the top-left image pixel and inspect which output changes.
# Expected: only output [0, 0] increases 10.

# Exercise 5: Count shared parameters
# Construct a bias-free Conv2D layer with 2 filters of size 2x2 on one input channel.
# Expected: 8 trainable scalars regardless of image height.

# Exercise 6: Add a constant image offset
# Add 100 to every pixel and compare outputs under the zero-sum kernel.
# Expected: output unchanged.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
