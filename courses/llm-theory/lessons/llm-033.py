"""llm-033: Preference objectives and what they do not prove.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Evaluate equal margins
# Set both policy and reference chosen-minus-rejected differences to1 withbeta.1.
# Expected: margin0 and losslog2.

# Exercise 2: Favor the chosen response
# Use policy difference2,reference difference0,beta.5.
# Expected: margin1;losslog(1+exp(-1)).

# Exercise 3: Reverse the labels
# Swap chosen and rejected while keeping their scores attached to the same response
# identities.
# Expected: margin-1 and larger loss.

# Exercise 4: Check numeric stability
# Evaluate margins1000 and-1000 withlogaddexp.
# Expected: finite losses approximately0 and1000.

# Exercise 5: Track pair identity
# Store response IDsr1,r2 and a preference label; reverse the label while retaining both
# identities.
# Expected: chosen identity changes tor2; scores remain keyed by ID.

# Exercise 6: Limit the claim
# Record that a preferred response may still contain a false factual statement.
# Expected: preference agreementTrue,factuality_verifiedFalse.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
