"""torch-008: One optimizer step you can audit.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate the initial loss
# Use float64 x1, 2, 3, y2x and scalar w0.
# Expected: mean squared loss 56/3.

# Exercise 2: Inspect the gradient before updating
# Back propagate the initial loss and compare with-56/3.
# Expected: gradient-56/3; weight still 0.

# Exercise 3: Apply exactly one SGD update
# Use SGD learning rate.1 onw and recompute the objective afterward.
# Expected: w28/15; loss 56/675.

# Exercise 4: Expose the broadcast counterexample
# At a fresh w0, compare vector predictions with column targets shaped(3, 1).
# Expected: initial loss still 56/3, but gradient-16.

# Exercise 5: Check a finite-difference gradient
# Use a plain NumPy scalar objective around w0 with h.001.
# Expected: slope-56/3 within 1e-9.

# Exercise 6: Clear the consumed gradient
# Call optimizer.zero_grad(set_to_none=True) after the step and inspect state.
# Expected: w.grad None; updated weight unchanged.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
