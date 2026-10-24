"""tf-028: Restartable training and checkpoint evidence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Create nontrivial optimizer state
# Take two Adam steps on(w-2)² fromw0 and inspect iterations.
# Expected: iteration count2 and positive weight.

# Exercise 2: Save both state components
# Save a checkpoint containingw and Adam into a TemporaryDirectory.
# Expected: checkpoint index exists; no course source file is written.

# Exercise 3: Calculate the uninterrupted control
# Snapshot the saved weight and take one further step without restoring.
# Expected: iteration count3; weight changes.

# Exercise 4: Restore in a fresh process
# Launch the existing interpreter with fresh variable/Adam objects, restore the saved
# prefix and take one step.
# Expected: child weight matches control within1e-6; child iterations3.

# Exercise 5: Expose a weights-only restart
# Set a fresh Adam variable to the saved weight without restoring optimizer moments, then
# take one step.
# Expected: next weight differs from the full-state control by more than1e-6.

# Exercise 6: Verify cleanup
# Remove the owned temporary checkpoint directory and verify it no longer exists.
# Expected: temporary checkpoint directory absent.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
