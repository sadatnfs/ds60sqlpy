"""torch-028: Restartable training, optimizer state and RNG evidence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Create nontrivial training state
# Take two Adam updates of a zero-weight linear model onx1, 2 andy2 x.
# Expected: optimizer step2 and positive weight.

# Exercise 2: Save the complete local contract
# Write model, optimizer, RNG and data_position2 into an owned temporary checkpoint.
# Expected: file exists and metadata position2.

# Exercise 3: Record uninterrupted continuation
# Draw three random values, then a small target perturbation, and perform the third
# update.
# Expected: finite weight, step3, and saved three-value random probe.

# Exercise 4: Restore in a fresh interpreter
# Recreate model and Adam, restore all state, repeat the same draws and update.
# Expected: probe matches and next weight agrees within1e-6; position3.

# Exercise 5: Expose a weights-only restart
# Restore only the saved model into fresh Adam and take the same third batch update.
# Expected: next weight differs from full-state continuation.

# Exercise 6: Verify cleanup and bounded claims
# Remove the owned checkpoint directory and report that the literal CPU batch contract was
# tested.
# Expected: directory absent; no distributed-loader claim.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
