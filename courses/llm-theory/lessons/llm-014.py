"""llm-014: Capstone: a small language-model evidence notebook.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count transitions in new documents
# Use vocabulary A=0, B=1, C=2 and the documents CAAB and BCA; count transitions within
# each document.
# Expected: C to A: 2, A to A: 1, A to B: 1, B to C: 1; total 5; no B to B transition across the document boundary.

# Exercise 2: Predict two smoothed rows
# Apply add-one smoothing to the new counts and predict the rows for contexts A and C.
# Expected: row A [2/5, 2/5, 1/5]; row C [3/5, 1/5, 1/5].

# Exercise 3: Score held-out transitions
# Evaluate held-out sequence A, C, B using the frozen table.
# Expected: 2 targets; NLL log 3+log 3.

# Exercise 4: Prove no assessment update
# Compare the count matrix before and after scoring.
# Expected: counts unchanged exactly.

# Exercise 5: Verify a causal prefix oracle
# For zero-score attention values 2, 4, 8 calculate prefix means and independently
# recompute each prefix.
# Expected: outputs 2, 3, 14/3.

# Exercise 6: Write the bounded comparison
# Create a report with vocabulary size 3, 2 held-out targets and a limitation about unseen
# tasks.
# Expected: report includes finite mean NLL and no broad competence claim.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
