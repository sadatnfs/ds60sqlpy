"""tf-016: Nonlinearity and initialization.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct XOR
# Evaluate two rectified differences on inputs(0,0),(0,1),(1,0),(1,1).
# Expected: outputs[0,1,1,0].

# Exercise 2: Remove the nonlinearity
# Sum the two raw difference columns before applying a threshold.
# Expected: all four sums0.

# Exercise 3: Compose affine matrices
# Multiply two fixed matrices and verify that a two-layer linear computation equals one
# matrix product.
# Expected: two paths agree within1e-6.

# Exercise 4: Inspect a dead region
# Evaluate ReLU and its tape gradient at-2 and+2.
# Expected: values[0,2], gradients[0,1].

# Exercise 5: Show symmetry
# Create two hidden units with identical columns and compare their activations on every
# XOR input.
# Expected: hidden columns match exactly.

# Exercise 6: Transfer outside the corners
# Evaluate the fixed construction at(.2,.8) and(.8,.2), and state what it computes away
# from binary inputs.
# Expected: both outputs.6; function is absolute difference.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
