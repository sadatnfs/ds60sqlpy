"""llm-015: PyTorch tensors and automatic gradients.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Derive a scalar gradient
# Differentiate(w-2)² atw0 in float64.
# Expected: gradient-4 and loss4.

# Exercise 2: Compare finite differences
# Use central differenceh=.001 for the same scalar function.
# Expected: finite difference approximately-4 within1e-10.

# Exercise 3: Observe accumulation
# Call backward on a new loss without clearing the prior gradient.
# Expected: stored gradient becomes-8.

# Exercise 4: Clear gradient state
# Set the gradient toNone, recompute and backpropagate once.
# Expected: gradient returns to-4.

# Exercise 5: Inspect detachment
# Detachw and compare its value and gradient-tracking status.
# Expected: same value0; requires_gradFalse.

# Exercise 6: Check an embedding table
# Lookup IDs2,0,2 in a fixed4x2 table and compare repeated rows.
# Expected: shape(3,2); rows0 and2 both[2,2].

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
