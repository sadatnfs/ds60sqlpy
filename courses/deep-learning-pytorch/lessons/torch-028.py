"""torch-028: Restartable training, optimizer state and RNG evidence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict Adam's first step
# From a fresh make_state(), take one step with zero noise and compare the weight with the
# learning rate 0.05.
# Expected: weight 0.05 within 1e-6.

# Exercise 2: Inspect the new optimizer state
# List the state entries Adam stores for that parameter after one step.
# Expected: keys step, exp_avg and exp_avg_sq; step equals 1.

# Exercise 3: Replay a saved random state
# Save torch.get_rng_state(), draw three values, restore the state and draw again.
# Expected: the two draws are identical.

# Exercise 4: Restore in a fresh interpreter
# Recreate model and Adam, restore all state, repeat the same draws and update.
# Expected: probe matches and next weight agrees within 1e-6; position 3.

# Exercise 5: Expose a weights-only restart
# Restore only the saved model into fresh Adam and take the same third batch update.
# Expected: next weight differs from full-state continuation.

# Exercise 6: Verify cleanup and bounded claims
# Remove the owned checkpoint directory and report that the literal CPU batch contract was
# tested.
# Expected: directory absent; no distributed-loader claim.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
