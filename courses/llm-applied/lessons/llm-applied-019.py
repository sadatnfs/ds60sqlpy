"""llm-applied-019: Preference optimization, DPO and the RLHF distinction.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate the equal-margin loss
# Set policy difference0, reference difference0, beta.5.
# Expected: losslog2.

# Exercise 2: Inspect the preference gradient
# Backpropagate the equal-margin loss.
# Expected: gradient-.25.

# Exercise 3: Perform an actual update
# TakeSGD.2 on the scalar policy difference and recompute the loss.
# Expected: difference.05; loss belowlog2.

# Exercise 4: Reverse the preference
# Atzero policy difference, reverse the chosen/rejected orientation and inspect the
# gradient.
# Expected: gradient+.25.

# Exercise 5: Separate objective and factual support
# Record a preferred fluent answer that invents a metric denominator.
# Expected: preferenceTrue; source_supportedFalse; not accepted as a grounded answer.

# Exercise 6: Name the unexecuted RLHF machinery
# Create an execution receipt distinguishing the scalar offline update from reward-model
# training and online policy optimization.
# Expected: offline updateTrue; reward_model_trainedFalse; online_rlFalse.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
