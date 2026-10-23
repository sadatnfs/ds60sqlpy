"""llm-048: Exact speculative decoding and cache rollback.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Prove one-step distribution preservation
# Usep[.5, .3, .2] andq[.2, .5, .3]; calculate acceptedmass, rejectionmass andresidual.
# Expected: acceptedmass[.2, .3, .2]; rejection.3; residual[1, 0, 0]; combinedmassp.

# Exercise 2: Exercise acceptance andcorrection paths
# Propose token1 withacceptancedraw.8, then token2 withdraw.5.
# Expected: token1 rejected andcorrected to0; token2 accepted.

# Exercise 3: Check an all-accepted round andbonus token
# Setdraft andtarget equal top; propose tokens0, 1 withdraws.1, .6, andusebonusdraw.7.
# Expected: emitted[0, 1, 1]; accepted_count2; no rejection.

# Exercise 4: Stop at the first rejection
# Useconstanttargetp, draftq, proposal draws.1, .3 andacceptance draws.2, .9.
# Expected: draft[0, 1]; acceptedprefix[0]; correction0; emitted[0, 0].

# Exercise 5: Rollback actual K/V arrays
# Startcacheprefix[2], appendthetwo proposals, thenrollbackandappend thecorrection;
# comparewithafreshcache[2, 0, 0].
# Expected: tokens, keys, values and attention output match a fresh cache; retaining a rejected token breaks parity.

# Exercise 6: Handle equality,EOS,budgets andinvalid support
# Checkp=q hasnoresidual, stoponanacceptedEOS2, capoutputat2 tokens, andreject a zero-
# probability draftproposal.
# Expected: rejection mass is0 and residual isNone; accepted EOS stops generation; the token cap is respected; unsupported proposals raiseValueError.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
