"""llm-applied-019: Preference optimization, DPO and the RLHF distinction.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate the equal-margin loss
# Set policy difference 0, reference difference 0, beta 0.5.
# Expected: loss log(2).

# Exercise 2: Inspect the preference gradient
# Backpropagate the equal-margin loss.
# Expected: gradient -0.25.

# Exercise 3: Perform an actual update
# Take one SGD step at learning rate 0.2 on the scalar policy difference and recompute the loss.
# Expected: difference 0.05; loss below log(2).

# Exercise 4: Reverse the preference
# At zero policy difference, reverse the chosen/rejected orientation and inspect the
# gradient.
# Expected: gradient +0.25.

# Exercise 5: Separate objective and factual support
# Record a preferred fluent answer that invents a metric denominator.
# Expected: preference True; source_supported False; not accepted as a grounded answer.

# Exercise 6: Name the unexecuted RLHF machinery
# Create an execution receipt distinguishing the scalar offline update from reward-model
# training and online policy optimization.
# Expected: offline update True; reward_model_trained False; online_rl False.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
