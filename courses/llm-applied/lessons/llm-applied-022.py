"""llm-applied-022: Structured tools for extraction, aggregation and data-science work.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Execute a bounded grouped mean
# Use rows A1, A3, B10 and the admitted group_mean request.
# Expected: A count 2 mean 2; B count 1 mean 10.

# Exercise 2: Reject an arbitrary operation
# Submit operation run_sql or an extra query field.
# Expected: ValueError before any computation.

# Exercise 3: Reject invalid numeric values
# Replace one value with True, NaN or None, then check large finite values and
# cancellation under the same numeric policy.
# Expected: invalid rows are rejected; equal 1e308 values have finite mean 1e308 and opposite values have mean 0.

# Exercise 4: Enforce identity and work limits
# Duplicate a1, then supply 21 unique rows.
# Expected: duplicate identity and row-limit violations rejected.

# Exercise 5: Verify an explanation against the artifact
# Check a proposed sentence saying group A mean 2 against the result; reject a
# proposed mean 20.
# Expected: 2 accepted; 20 mismatch.

# Exercise 6: Refuse an unsupported causal interpretation
# Attach a descriptive result to a claim that group caused the difference without
# assignment-design evidence.
# Expected: descriptive statistic available; causal claim not established.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
