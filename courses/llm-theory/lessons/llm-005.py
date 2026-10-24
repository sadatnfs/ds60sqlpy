"""llm-005: predict from the companion guide, then modify an owned copy."""

import math

probabilities = [0.5, 0.25]
total = -sum(math.log(p) for p in probabilities)
mean = total / 2
perplexity = math.exp(mean)
assert math.isclose(mean, 1.5 * math.log(2), rel_tol=0, abs_tol=1e-12)
assert math.isclose(perplexity, 2**1.5, rel_tol=0, abs_tol=1e-12)
print(total, mean, perplexity)

active_losses = [-math.log(0.5), -math.log(0.25)]
correct = sum(active_losses) / 2
wrong = sum(active_losses) / 3
assert math.isclose(correct, 1.5 * math.log(2), rel_tol=0, abs_tol=1e-12)
assert wrong < correct
print(correct, wrong)

# Exercise 1: Trace a perplexity
# Calculate total NLL, active count, mean NLL and perplexity for [0.5,0.25].
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct a masked score
# Implement score_targets; append probability 1 as ignored padding using mask
# [True,True,False].
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Compare document weighting
# Score document A=[0.5] and B=[0.25,0.25,0.25].
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Handle zero probability
# Score [0.5,0] with both targets active, then ignore the zero-probability slot.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Reject an absent or invalid score
# Try an all-false mask, an empty list, probability 1.1 and an integer mask.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Challenge a tokenizer ranking
# The same string cat is one token with probability 0.25 under A, or three character
# targets each probability 0.5 under B. Compare raw token perplexity and whole-string
# likelihood.
# Add your attempt and keep its observed values or exception beside your prediction.
