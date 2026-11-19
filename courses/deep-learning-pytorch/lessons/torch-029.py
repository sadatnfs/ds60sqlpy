"""torch-029: Stable objectives, precision and mixed-precision boundaries.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Find the float64 overflow boundary
# Exponentiate float64 values 709 and 710.
# Expected: \(e^{709}\) is finite (about 8.2e307); \(e^{710}\) overflows to inf.

# Exercise 2: Compute a stable loss for target 1
# Use float32 logits [1000, 998] with target class 1.
# Expected: loss \(\log(1+e^{2})\), about 2.1269, within 1e-5.

# Exercise 3: Check a new shift
# Compare the softmax of [1000, 998] with the softmax of [5, 3].
# Expected: both are about [0.8808, 0.1192] and match within 1e-6.

# Exercise 4: Inspect stable gradients
# Differentiate the target 0 loss with respect to both logits.
# Expected: finite gradients summing approximately 0.

# Exercise 5: Compare dtype ranges explicitly
# Inspect float16 and bfloat16 maximum values and float32 epsilon.
# Expected: bfloat16 range exceeds float16; float32 epsilon positive.

# Exercise 6: Reject a nonfinite input contract
# Pass a NaN logit through an explicit finite-input validator.
# Expected: ValueError before loss evaluation.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
