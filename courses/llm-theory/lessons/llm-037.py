"""llm-037: Evaluate retrieval and answers separately.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Classify four cases
# Useq1 retrieval miss,q2 unsupported answer,q3 correct abstention,q4 supported correct
# answer.
# Expected: one case in each named category.

# Exercise 2: Compute appropriate abstention
# Count correct abstentions separately from answered correctness.
# Expected: 1 correct abstention;1 correct answered case.

# Exercise 3: Attach a claim span
# Use documentd1 text red square has four sides and cite span square has four sides for
# that claim.
# Expected: span appears verbatim and supports the stated claim.

# Exercise 4: Reject a misleading citation
# Cite the same document for claim the square weighs10kg.
# Expected: citation exists but claim unsupported.

# Exercise 5: Use an oracle-context control
# Forq1 supply the authored relevant document and record whether the answer becomes
# correct.
# Expected: retrieval miss removed;answer outcome measured separately.

# Exercise 6: Preserve question identity
# Join observed and oracle results byq1 and reject duplicate IDs in a score table.
# Expected: one row per question;duplicateq1 detected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
