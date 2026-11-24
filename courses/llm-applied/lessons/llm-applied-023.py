"""llm-applied-023: Domain assistant boundaries: freshness, injection, budgets and traces.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Check evidence freshness
# Use fixed UTC now 2026-10-22 and a document published one day earlier under a two-day
# limit.
# Expected: fresh True.

# Exercise 2: Reject stale and future evidence
# Test a three-day-old document and a document dated one hour in the future.
# Expected: both fail freshness admission.

# Exercise 3: Enforce a three-call budget
# Consume exactly 3 operations, then attempt a fourth.
# Expected: used 3; fourth raises RuntimeError before increment.

# Exercise 4: Reject naive timestamp assumptions
# Pass a datetime without timezone information.
# Expected: ValueError.

# Exercise 5: Build an allowlisted trace
# Create a trace from metadata plus secret/source_text fields and inspect the output.
# Expected: only request_id, corpus_version, policy, result fields retained.

# Exercise 6: Make stale evidence produce abstention
# Combine authorized True with fresh False and require both before answering.
# Expected: answer admission False; reason stale evidence.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
