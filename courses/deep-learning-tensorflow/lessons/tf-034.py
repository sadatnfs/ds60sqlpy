"""tf-034: Robustness, privacy and model evidence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count errors by group
# Use groupsA,A,B with predictions1,0,0 and truth1,1,0.
# Expected: A1/2 errors; B0/1.

# Exercise 2: Expose duplicate confidence
# Repeat the groupB row five times and compare row count with unique IDs.
# Expected: 8 rows but only3 unique IDs.

# Exercise 3: Evaluate fixed perturbations
# Use f(x)=x>=0 with base1 and perturbations-.1,-.9,-1.1.
# Expected: first two retain class1; final perturbation changes to0.

# Exercise 4: Keep severities separate
# Record one severe failure and nine minor passes; count severe failures independently of
# total pass rate.
# Expected: 90percent passes and1 severe failure.

# Exercise 5: Write bounded claims
# Create a model card naming the three unique units and untested conditions.
# Expected: card includes count3 and an untested future-population condition.

# Exercise 6: Reject an empty group rate
# Compute a rate only when its group has observations.
# Expected: empty group producesNone, not0.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
