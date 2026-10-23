"""torch-034: Robustness, privacy and evidence beyond a score.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count group errors
# Use groups A, A, B with truth 1, 1, 0 and prediction 1, 0, 0.
# Expected: A1/2errors; B0/1.

# Exercise 2: Expose repeated identities
# Repeatcorrectrecordc five times and compare row count with unique IDs.
# Expected: 8rows but 3 unique IDs.

# Exercise 3: Trace a controlled perturbation
# Classify x>=0 at base 1 after shifts-.1, -.9, -1.1.
# Expected: labels 1, 1, 0.

# Exercise 4: Keep severe failures visible
# Use 9 minor passes and 1 severe failure.
# Expected: overall pass rate.9; severe failure count 1.

# Exercise 5: Represent an untested group
# Define a rate helper with count 0.
# Expected: None for untested; 0for zero errors in one case.

# Exercise 6: Write a bounded card
# Record 3 unique units, synthetic teaching use and untested future conditions.
# Expected: card explicitly has no privacy guarantee.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
