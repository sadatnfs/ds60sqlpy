"""tf-023: Debugging a custom training loop.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Expose a missing path
# Compute(w-2)² before opening a tape and ask that tape for its gradient.
# Expected: gradient is None.

# Exercise 2: Distinguish an actual zero
# Compute the same objective inside the tape at w=2.
# Expected: gradient is a tensor equal 0.

# Exercise 3: Repair two updates
# Use x = [1, 2, 3], y = 2x, w = 0 and rate 0.1 for exactly 2 steps.
# Expected: weight 448/225 within 1e-12.

# Exercise 4: Recompute loss after assignment
# Compare the two-step loss with the one-step loss 56/675.
# Expected: two-step loss is smaller and nonnegative.

# Exercise 5: Check gradient finiteness
# Inject a nonfinite target and refuse to apply its gradient.
# Expected: gradient is nonfinite and rejected before assignment.

# Exercise 6: Compare an analytic recurrence
# Calculate both updates with plain Python and compare each state with the tape trace.
# Expected: both recorded states match within 1e-12.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
