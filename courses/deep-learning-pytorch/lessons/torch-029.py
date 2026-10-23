"""torch-029: Stable objectives, precision and mixed-precision boundaries.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Expose naive overflow
# Exponentiate float32 logits1000, 999 directly.
# Expected: both exponentials infinite.

# Exercise 2: Compute a stable class loss
# Use target0 with the same logits.
# Expected: loss log(1+exp(-1)) within1e-6.

# Exercise 3: Check shift invariance
# Compare softmax1000, 999 with softmax0, -1.
# Expected: probabilities match within1e-6.

# Exercise 4: Inspect stable gradients
# Differentiate the target0 loss with respect to both logits.
# Expected: finite gradients summing approximately0.

# Exercise 5: Compare dtype ranges explicitly
# Inspect float16 andbfloat16 maximum values and float32 epsilon.
# Expected: bfloat16 range exceeds float16; float32 epsilon positive.

# Exercise 6: Reject a nonfinite input contract
# Pass aN aN logit through an explicit finite-input validator.
# Expected: ValueError before loss evaluation.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
