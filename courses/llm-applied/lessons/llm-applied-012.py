"""llm-applied-012: Evaluating retrieval and answers with oracle controls.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate recall and reciprocal rank
# Use relevant IDs a, c and retrieved b, c, a.
# Expected: recall1; reciprocal rank.5.

# Exercise 2: Measure a retrieval miss
# Use relevant a and retrieved b, c.
# Expected: recall0; reciprocal rank 0.

# Exercise 3: Handle an unanswerable question
# Use an empty relevant set and a saved abstention result.
# Expected: recallNone; appropriate abstentionTrue.

# Exercise 4: Separate support from correctness
# Record a correct-looking answer whose cited context does not support it.
# Expected: correctTrue but supportedFalse.

# Exercise 5: Apply an oracle-context control
# Compare q1 observed incorrect with oracle-context correct under the same rubric.
# Expected: paired improvement1 for q1.

# Exercise 6: Reject duplicate result identities
# Validate one score row per question and inject a duplicateq1.
# Expected: duplicate ID detected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
