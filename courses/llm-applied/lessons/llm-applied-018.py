"""llm-applied-018: Compare full and adapter fine-tuning on frozen tasks.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Clone one base into two candidates
# Create a seed 31 decoder and copy its state into full and adapted candidates.
# Expected: all initial base parameters equal.

# Exercise 2: Install an output-head adapter
# Freeze the adapted model, replace its output layer withrank2LoRA, and compare initial
# logits.
# Expected: 96 trainable adapter entries; initial logits match base.

# Exercise 3: Train both candidates under fixed budgets
# Run20 full-SFT updates at.01 and20 adapter updates at.03 on the same masked batch.
# Expected: both training losses decrease; all logged values finite.

# Exercise 4: Prove base preservation
# Compare every frozen adapted-model parameter against its saved copy.
# Expected: all frozen tensors exactly equal.

# Exercise 5: Compare a frozen held-out task
# Evaluate prompt[7, 2] withanswer[5, 3] for both candidates using the same mask.
# Expected: two finite held-out losses; no predetermined winner.

# Exercise 6: Record comparison limits
# Build a report with trainable counts, update budgets, target module and task scope.
# Expected: adapter96 entries; 20 updates each; scope literal-token task.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
