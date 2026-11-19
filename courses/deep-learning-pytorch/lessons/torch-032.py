"""torch-032: state_dict, torch.export and inference parity.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a new inference output
# Set a bias-free 2-to-1 Linear weight to [1, 3] and predict the rows [1, 2] and [3, 4].
# Expected: outputs [[7], [15]].

# Exercise 2: Load state into matching and mismatched modules
# Load the model's state_dict into a fresh bias-free Linear(2, 1) and into a Linear(2, 1)
# that has a bias.
# Expected: the matching module reproduces the outputs; the module with a bias raises RuntimeError for the missing key.

# Exercise 3: Export the new model in memory
# Export the new model for the two-row input and compare the exported module's
# predictions.
# Expected: exported predictions match [[7], [15]] within 1e-6.

# Exercise 4: Check both artifacts in a fresh process
# Load the state and exported program in a new interpreter and compare outputs.
# Expected: both child predictions 0, 2.

# Exercise 5: Expose static batch specialization
# Pass three rows to the statically exported module and compare with ordinary Linear.
# Expected: ordinary Linear accepts 3; static export rejects its batch constraint.

# Exercise 6: Declare a bounded dynamic batch and clean up
# Export with batch Dim range 1..4, test three rows, and remove owned files.
# Expected: three-row parity passes; temporary directory absent.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
