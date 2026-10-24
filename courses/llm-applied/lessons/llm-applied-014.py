"""llm-applied-014: Supervised fine-tuning data and answer-target masks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align an answer-only record
# Use promptIDs[1, 2] andanswerIDs[5, 6, 3].
# Expected: inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.

# Exercise 2: Preserve prompt context without prompt loss
# Change promptIDs to[8, 9] while retaining the answer; inspect labels.
# Expected: prompt inputs change; answer labels remain5, 6, 3.

# Exercise 3: Reject an empty answer
# Prepare a record with prompt[1, 2] and no answer tokens.
# Expected: ValueError for no answer targets.

# Exercise 4: Detect destructive truncation
# Use a context limit2 for a prompt oflength2 and answerlength3.
# Expected: ValueError because truncation removes every answer target.

# Exercise 5: Keep family splits disjoint
# Assign two formatting variants tofamilyF and test that they cannot cross train/test.
# Expected: family intersectionF is a leak.

# Exercise 6: Reject unsupported targets before training
# Mark a target answer as unsupported by its cited source and apply an admission gate.
# Expected: record excluded despite valid token arrays.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
