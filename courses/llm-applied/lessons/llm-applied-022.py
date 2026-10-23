"""llm-applied-022: Structured tools for extraction, aggregation and data-science work.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Execute a bounded grouped mean
# Use rowsA1, A3, B10 and the admittedgroup_mean request.
# Expected: A count 2 mean2; B count 1 mean10.

# Exercise 2: Reject an arbitrary operation
# Submitoperationrun_sql or an extraquery field.
# Expected: ValueError before any computation.

# Exercise 3: Reject invalid numeric values
# Replace onevalue withTrue, NaN orNone under the strict numeric policy.
# Expected: each invalid row is rejected.

# Exercise 4: Enforce identity and work limits
# Duplicatea1, then supply21 unique rows.
# Expected: duplicate identity and row-limit violations rejected.

# Exercise 5: Verify an explanation against the artifact
# Check a proposed sentence saying groupAmean2 against the result; reject a
# proposedmean20.
# Expected: 2accepted; 20mismatch.

# Exercise 6: Refuse an unsupported causal interpretation
# Attach a descriptive result to a claim that group caused the difference without
# assignment-design evidence.
# Expected: descriptive statisticavailable; causal claimnot established.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
