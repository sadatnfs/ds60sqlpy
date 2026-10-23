"""llm-applied-002: Data-science task contracts and structured extraction.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Validate a correct proposal
# Validate visits 10, purchases 3 and assignment_unit account.
# Expected: conversion rate 0.3.

# Exercise 2: Reject a plausible but impossible record
# Validate visits 2 and purchases 3 under the declared one-purchase-per-visit policy.
# Expected: ValueError for inconsistent counts.

# Exercise 3: Trace extracted values to text
# Parse the source text Visits: 10; Purchases: 3; Unit: account and retain source spans.
# Expected: values10 and3; each span slices the original digits.

# Exercise 4: Distinguish missing from zero
# Submit a record with purchases=None and compare it with a real zero-purchase record.
# Expected: None is rejected by this strict schema; zero is accepted with rate 0.

# Exercise 5: Reject boolean and extra fields
# Submit visits=True, then add an undeclared p_value field to a valid proposal.
# Expected: TypeError for a boolean count; ValueError for an extra field.

# Exercise 6: Preserve the assignment unit
# Attempt to replace account with visit and explain why the independence assumption cannot
# be inferred from the count fields.
# Expected: invalid unit rejected; account remains explicit.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
