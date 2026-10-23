"""llm-045: Pre/post normalization, RMSNorm and gated feed-forward networks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare RMSNorm andLayerNorm
# Normalizevector3, 4 withunitgain andepsilon1e-8.
# Expected: RMSNorm mean nonzero; LayerNorm meanapproximately0.

# Exercise 2: Trace pre/post residual Jacobians
# Set thetransformedbranch tozero andcomparepre-normx withpost-normLayerNorm(x).
# Expected: pre-norm Jacobian is identity; post-norm Jacobian annihilates a constant feature shift.

# Exercise 3: Calculate a SwiGLU gate derivative
# Use scalar g0, u2 andoutputSiLU(g)*u.
# Expected: output0; gradientwithrespecttog1; withrespecttou0.

# Exercise 4: Check the RMSNorm Jacobian formula
# Compareautograd withJ=I/r-xxT/(d*r³) atx1, 2, 3.
# Expected: matricesagreewithin1e-10.

# Exercise 5: Match feed-forward parameter budgets
# CompareplainFFNwidthd4, hidden6 withSwiGLUhidden4, excludingbiases;
# executea4-to-4gatedblock.
# Expected: both48weightentries; outputshape(2, 4).

# Exercise 6: Test invariance andzero-vector boundaries
# Shiftx1, 2, 3 by 5, comparethetwo normalizers, andnormalizezero.
# Expected: LayerNormshiftinvariant; RMSNormchanges; bothzerocasesfinite.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
