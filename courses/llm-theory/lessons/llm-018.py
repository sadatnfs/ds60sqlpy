"""llm-018: A bounded training loop with visible state.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Prepare a tiny training batch
# Use two four-token sequences and shifted labels with vocabulary16.
# Expected: inputs shape(2,3);6 active targets.

# Exercise 2: Measure the initial objective
# Calculate initial cross entropy before any optimizer step.
# Expected: finite positive loss.

# Exercise 3: Perform twelve bounded updates
# Use Adam(.01), zero gradients each step, log losses and norms, and update exactly12
# times.
# Expected: 12 finite losses and norms; at least one positive norm.

# Exercise 4: Verify actual parameter change
# Compare the output projection with its detached snapshot.
# Expected: weights differ.

# Exercise 5: Clear accumulated gradients
# Call zero_grad(set_to_none=True) after the run and inspect every parameter gradient.
# Expected: all gradientsNone.

# Exercise 6: Report budget honestly
# Create a run record with12 completed updates and the declared200 maximum.
# Expected: stopped_at12; no convergence claim.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
