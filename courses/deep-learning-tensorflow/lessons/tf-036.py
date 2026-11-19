"""tf-036: Capstone: release a small, reproducible model.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Build a literal model bundle
# Create a float32 two-feature model with coefficient [2, -1] and schema width 2.
# Expected: probe [3, 4] predicts 2.

# Exercise 2: Freeze and hash a split manifest
# Hash train IDs [a, b] and test IDs [c, d] using canonical JSON.
# Expected: disjoint IDs and a 64-character SHA256.

# Exercise 3: Catch tampered lineage
# Change one test ID and compare the resulting digest.
# Expected: digest differs.

# Exercise 4: Block incompatible schemas
# Compare an incoming three-feature schema with the frozen two-feature schema before
# prediction.
# Expected: schema gate is False.

# Exercise 5: Make the decision fail closed
# Evaluate required gates with an unexecuted restart proof represented as None, then with
# an actual failed schema gate.
# Expected: both decisions no-go.

# Exercise 6: Retain a rollback decision
# Construct a release record with previous artifact ID, holdout count and limits; keep no-
# go when any gate fails.
# Expected: decision no-go and previous artifact v1 retained.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
