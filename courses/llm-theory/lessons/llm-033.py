"""llm-033: Preference objectives and what they do not prove.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute a margin from log probabilities
# Use policy log probabilities -1 (chosen) and -4 (rejected), reference -2 and -3, and
# beta 0.25.
# Expected: margin 0.5; loss \(\log(1+e^{-0.5})\approx 0.474\), below \(\log 2\).

# Exercise 2: Predict the effect of beta
# Keep the same log probabilities and raise beta to 1. Predict the margin and whether the
# loss rises or falls.
# Expected: margin 2; loss \(\log(1+e^{-2})\approx 0.127\), smaller than at beta 0.25.

# Exercise 3: Reverse the labels
# Swap chosen and rejected while keeping their scores attached to the same response
# identities.
# Expected: margin -1 and larger loss.

# Exercise 4: Check numeric stability
# Evaluate margins 1000 and -1000 with logaddexp.
# Expected: finite losses approximately 0 and 1000.

# Exercise 5: Track pair identity
# Store response IDs r1, r2 and a preference label; reverse the label while retaining both
# identities.
# Expected: chosen identity changes to r2; scores remain keyed by ID.

# Exercise 6: Limit the claim
# Record that a preferred response may still contain a false factual statement.
# Expected: preference agreement True, factuality_verified False.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
