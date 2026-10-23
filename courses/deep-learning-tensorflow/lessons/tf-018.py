"""tf-018: Normalization state and batch dependence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Update moving state
# Apply BatchNorm with momentum.5 to rows[1,3],[3,5].
# Expected: moving mean[1,2].

# Exercise 2: Freeze evaluation state
# Call BatchNorm in evaluation with a very different batch and compare moving means.
# Expected: state remains[1,2].

# Exercise 3: Test row independence
# Apply LayerNorm to one row and to the same row beside[100,200].
# Expected: first row matches within1e-6.

# Exercise 4: Expose batch dependence
# Compare raw batch-centered first rows before and after adding an extreme row.
# Expected: first row changes from[-1,-1] to[-33,-66].

# Exercise 5: Repeat the state update
# Apply the original batch a second time in training mode.
# Expected: moving mean[1.5,3].

# Exercise 6: Handle a constant feature row
# Normalize a row[5,5] with LayerNorm and default zero offset.
# Expected: finite output[0,0].

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
