"""llm-023: Top-p, termination and decoding failure cases.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Retain the crossing token
# Apply top-p.6 to probabilities[.5,.3,.2].
# Expected: retained IDs0,1 with original mass.8.

# Exercise 2: Renormalize retained mass
# Normalize the selected two probabilities before drawing.
# Expected: probabilities.625,.375.

# Exercise 3: Reproduce local sampling
# Draw8 tokens with two independently seeded CPU generators.
# Expected: draw sequences match and contain only0,1.

# Exercise 4: Stop on EOS
# Consume proposed tokens2,3,9,4 with EOS9 and cap5.
# Expected: generated2,3,9;4 is never consumed.

# Exercise 5: Enforce a cap without EOS
# Consume an endless repeated token2 under cap3.
# Expected: exactly3 generated tokens.

# Exercise 6: Separate greedy mode
# Handle temperature0 with argmax rather than division.
# Expected: token0 and finite untouched logits.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
