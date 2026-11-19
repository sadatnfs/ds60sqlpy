"""llm-027: Calibration and comparable evaluation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Weight three documents
# Combine document mean losses 2, 4 and 1 with token counts 2, 1 and 5.
# Expected: token-weighted mean 13/8 = 1.625; document mean 7/3, about 2.333.

# Exercise 2: Summarize a second calibration bin
# Use confidences 0.9, 0.9, 0.7, 0.9, 0.6 with correctness 1, 0, 1, 1, 0 in a single bin.
# Expected: count 5, mean confidence 0.8, accuracy 0.6: overconfident by 0.2.

# Exercise 3: Represent an empty bin
# Select confidence values below 0.5 and summarize without fabricating a rate.
# Expected: count 0 and accuracy None.

# Exercise 4: Check boundary membership
# Use bins [0.5, 0.8) and [0.8, 1] on the fixture.
# Expected: counts 1 and 3, total 4.

# Exercise 5: Align paired errors
# Compare dictionaries A q1=0, q2=1 and B q2=0, q1=1 by IDs.
# Expected: differences [-1, 1], mean 0.

# Exercise 6: Reject incompatible tokenizer scores
# Compare evaluation metadata with tokenizer hash v1 versus v2.
# Expected: direct token-loss comparison marked incompatible.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
