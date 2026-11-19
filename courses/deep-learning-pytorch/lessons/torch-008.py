"""torch-008: One optimizer step you can audit.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute a new initial loss
# Use float64 x = 1, 2, targets y = 3x and scalar w = 0, and calculate the mean squared
# loss.
# Expected: loss 22.5.

# Exercise 2: Predict the gradient before stepping
# Backpropagate the new loss and compare the gradient with your hand calculation before
# any update.
# Expected: gradient -15; w still 0.

# Exercise 3: Apply one step with a new rate
# Take one SGD step with learning rate 0.05 and recompute the loss.
# Expected: w = 0.75; loss 12.65625.

# Exercise 4: Expose the broadcast counterexample
# At a fresh w = 0, compare vector predictions with column targets shaped (3, 1).
# Expected: initial loss still 56/3, but gradient -16.

# Exercise 5: Check a finite-difference gradient
# Use a plain NumPy scalar objective around \(w=0\) with finite-difference step
# \(h=0.001\).
# Expected: slope -56/3 within 1e-9.

# Exercise 6: Clear the consumed gradient
# Call `optimizer.zero_grad(set_to_none=True)` after the step and inspect state.
# Expected: w.grad None; updated weight unchanged.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
