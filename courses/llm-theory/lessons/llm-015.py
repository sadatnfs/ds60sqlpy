"""llm-015: PyTorch tensors and automatic gradients.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Derive a scalar gradient
# Differentiate(w-2)² at w=0 in float64.
# Expected: gradient -4 and loss 4.

# Exercise 2: Compare finite differences
# Use central difference h=0.001 for the same scalar function.
# Expected: finite difference approximately -4 within 1e-10.

# Exercise 3: Observe accumulation
# Call backward on a new loss without clearing the prior gradient.
# Expected: stored gradient becomes -8.

# Exercise 4: Clear gradient state
# Set the gradient to None, recompute and backpropagate once.
# Expected: gradient returns to -4.

# Exercise 5: Inspect detachment
# Detach w and compare its value and gradient-tracking status.
# Expected: same value 0; requires_gradFalse.

# Exercise 6: Check an embedding table
# Lookup IDs 2, 0, 2 in a fixed 4x2 table and compare repeated rows.
# Expected: shape (3, 2); rows 0 and 2 both [2, 2].

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
