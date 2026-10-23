"""torch-002: Tensors, devices, dtypes, strides and views.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Inspect shape and stride
# Create a2x3 float64 CPU tensor from values 0..5.
# Expected: shape(2, 3), stride(3, 1), CPU, float64.

# Exercise 2: Expose shared storage
# Slice the first row, change its first value, and inspect the original tensor.
# Expected: original x[0, 0] becomes 99.

# Exercise 3: Create an independent copy
# Clone the tensor, change the clone and compare the original.
# Expected: clone starts-1; original remains 99.

# Exercise 4: Trace a transposed layout
# Transpose x and inspect shape, strides and contiguity.
# Expected: shape(3, 2), stride(1, 3), noncontiguous.

# Exercise 5: Detect a pairing broadcast
# Subtract vector[1, 2, 3] from its column representation and inspect the result.
# Expected: shape(3, 3), while equal-vector subtraction has shape(3, ).

# Exercise 6: Reject incompatible arithmetic
# Add tensors shaped(2, 3) and(4, ) and capture the shape failure.
# Expected: RuntimeError for incompatible trailing dimensions.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
