"""torch-005: Derivatives, requires_grad and finite-difference checks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Derive a scalar slope
# Differentiate (w-2)**2 at w=0 using autograd.grad.
# Expected: derivative -4; loss 4.

# Exercise 2: Check three finite differences
# Use h=0.1, .01, .001 at w=0 and compare each slope with-4.
# Expected: all agree within 1e-10.

# Exercise 3: Separate gradient from update
# Use learning rate.1 and gradient-4 from w0.
# Expected: new w=0.4, not-4.

# Exercise 4: Inspect a stationary point
# Differentiate the same objective atw 2.
# Expected: gradient 0 and loss 0.

# Exercise 5: Observe grad-return behavior
# Check that autograd.grad did not accumulate into the leaf.grad field.
# Expected: w.grad is None despite a returned derivative.

# Exercise 6: Reject invalid probes
# Pass h=0, negative h and a function returning infinity to the finite-difference helper.
# Expected: all raise ValueError.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
