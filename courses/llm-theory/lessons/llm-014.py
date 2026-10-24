"""llm-014: Capstone: a small language-model evidence notebook.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Fit a tiny baseline
# Use vocabularyA,B,C and documentsABAB,AC; count transitions within documents.
# Expected: AtoB2,BtoA1,AtoC1; total4.

# Exercise 2: Normalize smoothed rows
# Apply add-one smoothing to the count matrix.
# Expected: row sums1; unseen C context is uniform.

# Exercise 3: Score held-out transitions
# Evaluate held-out sequenceA,C,B using the frozen table.
# Expected: 2 targets; NLL log3+log3.

# Exercise 4: Prove no assessment update
# Compare the count matrix before and after scoring.
# Expected: counts unchanged exactly.

# Exercise 5: Verify a causal prefix oracle
# For zero-score attention values2,4,8 calculate prefix means and independently recompute
# each prefix.
# Expected: outputs2,3,14/3.

# Exercise 6: Write the bounded comparison
# Create a report with vocabulary size3,2 held-out targets and a limitation about unseen
# tasks.
# Expected: report includes finite meanNLL and no broad competence claim.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
