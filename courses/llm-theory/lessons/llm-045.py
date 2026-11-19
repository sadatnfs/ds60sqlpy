"""llm-045: Pre/post normalization, RMSNorm and gated feed-forward networks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare RMSNorm and LayerNorm
# Normalize the vector [3, 4] with unit gain and epsilon 1e-8.
# Expected: RMSNorm mean nonzero; LayerNorm mean approximately 0.

# Exercise 2: Trace pre/post residual Jacobians
# Set the transformed branch to zero and compare pre-norm x with post-norm LayerNorm(x).
# Expected: pre-norm Jacobian is identity; post-norm Jacobian annihilates a constant feature shift.

# Exercise 3: Calculate a SwiGLU gate derivative
# Use scalar g=0, u=2 and output SiLU(g)*u.
# Expected: output0; gradient with respect to g is 1; with respect to u is 0.

# Exercise 4: Check the RMSNorm Jacobian formula
# Compare autograd with J=I/r-xxT/(d*r³) at x = [1, 2, 3].
# Expected: matrices agree within 1e-10.

# Exercise 5: Match feed-forward parameter budgets
# Compare plain FFN model width d=4, hidden6 with SwiGLU hidden width 4, excluding biases;
# execute a gated block with input and output width 4.
# Expected: both 48 weight entries; output shape(2, 4).

# Exercise 6: Test invariance and zero-vector boundaries
# Shift x = [1, 2, 3] by 5, compare the two normalizers, and normalize zero.
# Expected: LayerNorm shift invariant; RMSNorm changes; both zero cases finite.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
