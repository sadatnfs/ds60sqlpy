"""torch-032: state_dict, torch.export and inference parity.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Create a known inference model
# Set a 2-to-1 bias-free Linear weight to[2, -1] and predict rows 1, 2 and 3, 4.
# Expected: outputs 0, 2.

# Exercise 2: Round-trip named state
# Save state_dict to an owned temporary file, reconstruct the architecture and load
# weights_only.
# Expected: restored predictions match within 1e-6.

# Exercise 3: Save an exported program
# Export the fixed batch program, save it, and load its module.
# Expected: exported predictions match within 1e-6.

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
