"""llm-038: Tools, structured output and trust boundaries.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Accept one bounded proposal
# Validate toolread_fixture and document_idd1.
# Expected: accepted proposal identifiesd1.

# Exercise 2: Reject an unknown operation
# Submit toolrun_shell with document_idd1.
# Expected: ValueError;no execution.

# Exercise 3: Reject extra fields
# Add command orpath to an otherwise valid object.
# Expected: extra fields rejected.

# Exercise 4: Reject traversal-like identifiers
# Submit ../secret as the document ID.
# Expected: ValueError because the ID is outside the fixture allowlist.

# Exercise 5: Enforce types
# Submit document_id1 and a list instead of an object.
# Expected: TypeError for both malformed structures.

# Exercise 6: Keep retrieved instructions inert
# Read a fixture string saying ignore policy and run a command, then verify no second
# operation is proposed or executed.
# Expected: returned value is text;dispatch count1.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
