"""llm-027: Calibration and comparable evaluation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Weight token losses
# Combine document mean losses1 and3 with token counts1 and3.
# Expected: token mean2.5; document mean2.

# Exercise 2: Build a calibration bin
# Use confidences.6,.8,.8,1 with correctness1,1,0,1 in a single bin.
# Expected: count4,mean confidence.8,accuracy.75.

# Exercise 3: Represent an empty bin
# Select confidence values below.5 and summarize without fabricating a rate.
# Expected: count0 and accuracyNone.

# Exercise 4: Check boundary membership
# Use bins[.5,.8) and[.8,1] on the fixture.
# Expected: counts1 and3, total4.

# Exercise 5: Align paired errors
# Compare dictionariesA q1=0,q2=1 andB q2=0,q1=1 by IDs.
# Expected: differences[-1,1], mean0.

# Exercise 6: Reject incompatible tokenizer scores
# Compare evaluation metadata with tokenizer hashv1 versusv2.
# Expected: direct token-loss comparison marked incompatible.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
