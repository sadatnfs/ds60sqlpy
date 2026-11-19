"""torch-002: Tensors, devices, dtypes, strides and views.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a 3-by-2 layout
# Create a float32 CPU tensor from values 0..5 reshaped to (3, 2) and predict its stride
# before printing it.
# Expected: shape (3, 2), stride (2, 1), float32 on CPU.

# Exercise 2: Write through a column view
# Take column 1 of the (3, 2) tensor as a view, set its last entry to -7 and inspect the
# original tensor and the view's stride.
# Expected: grid[2, 1] becomes -7; the column view has stride (2,).

# Exercise 3: Separate contiguous from clone
# Call contiguous() and clone() on the already contiguous grid, then write 100 into the
# [0, 0] entry of the first result and -100 into the second.
# Expected: contiguous() returns the same storage, so grid[0, 0] becomes 100; the clone write leaves grid unchanged.

# Exercise 4: Trace a transposed layout
# Transpose x and inspect shape, strides and contiguity.
# Expected: shape (3, 2), stride (1, 3), noncontiguous.

# Exercise 5: Detect a pairing broadcast
# Subtract vector [1, 2, 3] from its column representation and inspect the result.
# Expected: shape (3, 3), while equal-vector subtraction has shape (3, ).

# Exercise 6: Reject incompatible arithmetic
# Add tensors shaped (2, 3) and (4, ) and capture the shape failure.
# Expected: RuntimeError for incompatible trailing dimensions.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
