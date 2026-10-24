"""tf-029: Precision, overflow and stable objectives.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Expose naive overflow
# Exponentiate NumPy logits[1000,999] directly under an explicit error-state context.
# Expected: both exponentials are infinite.

# Exercise 2: Calculate stable loss
# Use a logits-aware TensorFlow loss for target0.
# Expected: losslog(1+exp(-1)) within1e-6.

# Exercise 3: Check shift invariance
# Compare softmax[1000,999] with softmax[0,-1].
# Expected: probabilities agree within1e-6.

# Exercise 4: Inspect gradients
# Differentiate the stable target0 loss with respect to both logits.
# Expected: finite gradients summing approximately0.

# Exercise 5: Separate precision policies
# Compare float16 and float64 exponentiation of20.
# Expected: float16 overflows; float64 remains finite.

# Exercise 6: Validate input finiteness
# Reject a NaN logit before using a maximum-subtracted softmax helper.
# Expected: ValueError for NaN; finite input returns unit mass.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
