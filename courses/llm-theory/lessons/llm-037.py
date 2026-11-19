"""llm-037: Evaluate retrieval and answers separately.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Classify five new cases
# Use r1 and r2 retrieval misses, r3 an unsupported answer, r4 a correct supported answer
# and r5 an abstention on an answerable question.
# Expected: 2 retrieval misses, 1 unsupported answer, 1 abstention that was not appropriate and 1 correct answer.

# Exercise 2: Predict coverage and answered accuracy
# From the five new cases, compute the share of questions answered and the accuracy among
# answered questions.
# Expected: coverage 0.8; answered accuracy 0.25.

# Exercise 3: Attach a claim span
# Use document d1 text red square has four sides and cite span square has four sides for
# that claim.
# Expected: span appears verbatim and supports the stated claim.

# Exercise 4: Reject a misleading citation
# Cite the same document for claim the square weighs 10 kg.
# Expected: citation exists but claim unsupported.

# Exercise 5: Use an oracle-context control
# For q1 supply the authored relevant document and record whether the answer becomes
# correct.
# Expected: retrieval miss removed; answer outcome measured separately.

# Exercise 6: Preserve question identity
# Join observed and oracle results by q1 and reject duplicate IDs in a score table.
# Expected: one row per question; duplicate q1 detected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
