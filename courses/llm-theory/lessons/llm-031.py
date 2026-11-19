"""llm-031: Instruction tuning and loss masks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align the target mask
# Use sequence [1, 2, 5, 6, 3], where 1, 2 are prompt and 5, 6, 3 answer.
# Expected: targets [2, 5, 6, 3]; mask [False, True, True, True].

# Exercise 2: Compute answer-only loss
# Use zero vocabulary 8 logits and replace prompt targets with -100.
# Expected: 3 active targets; mean \(\log 8\).

# Exercise 3: Compare loss sums
# Calculate full-sequence and answer-only summed losses.
# Expected: 4 log 8 versus 3 log 8.

# Exercise 4: Inspect ignored gradients
# Backpropagate answer-only loss and examine the first logit position.
# Expected: first-position gradient all zero; answer gradients nonzero.

# Exercise 5: Detect template leakage
# Assign two paraphrased prompts to family T and split them across train/test.
# Expected: family intersection T.

# Exercise 6: Refuse missing answers
# Set an all-false answer mask and check the denominator before training.
# Expected: no active answer targets; explicit ValueError.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
