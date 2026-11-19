"""llm-023: Top-p, termination and decoding failure cases.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Retain the crossing token
# Apply top-p 0.6 to probabilities [0.5, 0.3, 0.2].
# Expected: retained IDs 0, 1 with original mass 0.8.

# Exercise 2: Renormalize retained mass
# Normalize the selected two probabilities before drawing.
# Expected: probabilities 0.625, 0.375.

# Exercise 3: Reproduce local sampling
# Draw 8 tokens with two independently seeded CPU generators.
# Expected: draw sequences match and contain only 0, 1.

# Exercise 4: Stop on EOS
# Consume proposed tokens 2, 3, 9, 4 with EOS ID 9 and cap 5.
# Expected: generated 2, 3, 9; 4 is never consumed.

# Exercise 5: Enforce a cap without EOS
# Consume an endless repeated token 2 under cap 3.
# Expected: exactly 3 generated tokens.

# Exercise 6: Separate greedy mode
# Handle temperature 0 with argmax rather than division.
# Expected: token 0 and finite untouched logits.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
