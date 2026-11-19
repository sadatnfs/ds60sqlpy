"""llm-048: Exact speculative decoding and cache rollback.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Prove one-step distribution preservation
# Use target p = [0.5, 0.3, 0.2] and draft q = [0.2, 0.5, 0.3]; calculate the accepted
# mass, rejection mass and residual.
# Expected: accepted mass[.2, .3, .2]; rejection .3; residual[1, 0, 0]; combined mass p.

# Exercise 2: Exercise acceptance and correction paths
# Propose token 1 with acceptance draw .8, then token 2 with draw .5.
# Expected: token 1 rejected and corrected to 0; token 2 accepted.

# Exercise 3: Check an all-accepted round and bonus token
# Set draft and target both equal to p; propose tokens 0, 1 with draws 0.1, 0.6, and use
# bonus draw 0.7.
# Expected: emitted[0, 1, 1]; accepted_count2; no rejection.

# Exercise 4: Stop at the first rejection
# Use constant target p, draft q, proposal draws 0.1, 0.3 and acceptance draws 0.2, 0.9.
# Expected: draft[0, 1]; accepted prefix[0]; correction 0; emitted[0, 0].

# Exercise 5: Rollback actual K/V arrays
# Start with cache prefix [2], append the two proposals, then roll back and append the
# correction; compare with a fresh cache [2, 0, 0].
# Expected: tokens, keys, values and attention output match a fresh cache; retaining a rejected token breaks parity.

# Exercise 6: Handle equality, EOS, budgets and invalid support
# Check that p=q has no residual, stop on an accepted EOS 2, cap output at 2 tokens, and
# reject a zero-probability draft proposal.
# Expected: rejection mass is 0 and residual is None; accepted EOS stops generation; the token cap is respected; unsupported proposals raise ValueError.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
