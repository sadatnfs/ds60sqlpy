"""llm-042: Capstone: a defensible language-system decision.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze common questions
# Define q1 answerable square sides, q2 answerable circle color, q3 missing comet period
# with stable families.
# Expected: 3 distinct questions and a missing-evidence case.

# Exercise 2: Compare saved candidate decisions
# Use per-question correctness tiny [1, 0, 0], count [0, 0, 0], retrieval [1, 1, 1], where
# q3 correctmeansabstaining.
# Expected: scores 1/3, 0/3, 3/3 on this fixture only.

# Exercise 3: Run model mechanism checks
# Initialize the small decoder and compare full-prefix and incremental cached logits on 2,
# 5, 7.
# Expected: parity within 1e-6; parameters below 50000.

# Exercise 4: Bind lineage and budgets
# Hash model parameter bytes and record fixture hash, context 3 and generated-token cap 4.
# Expected: two 64-character hashes and cap 4.

# Exercise 5: Apply an honest release gate
# Set mechanism True, trust-boundary True, heldout-population evidence None and severe-
# failure gate False.
# Expected: decision no-go.

# Exercise 6: Write the reviewer decision
# Record one failure example, missing evidence and next action beside the no-go.
# Expected: report names q3 unsupported answer and new independent families needed.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
