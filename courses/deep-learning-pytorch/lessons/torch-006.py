"""torch-006: Autograd graphs, the chain rule and in-place hazards.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Trace the chain rule
# Use w=1, z=2*w, a=z*z and loss=(a-1)**2.
# Expected: z2, a4, loss9, gradient48.

# Exercise 2: Check an independent slope
# Compare the chain derivative with a central difference of the complete scalar
# expression.
# Expected: approximately48 within1e-5.

# Exercise 3: Observe a leaf mutation guard
# Try an in-place add on a leaf requiring gradients outside no_grad.
# Expected: RuntimeError.

# Exercise 4: Expose saved-value invalidation
# Build loss=x*x, mutate x under no_grad before backward, and inspect the failure.
# Expected: RuntimeError from a changed saved tensor version.

# Exercise 5: Inspect a ReLU convention
# Differentiate ReLU at negative, zero and positive inputs.
# Expected: gradients0, 0, 1.

# Exercise 6: Recompute after an update
# Update a scalar under no_grad, then build a fresh quadratic objective and request its
# derivative.
# Expected: at new w=1.5, gradient -1 for (w-2)**2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
