"""llm-038: Tools, structured output and trust boundaries.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Accept the second allowed document
# Validate tool read_fixture with document_id d2 and check whether the returned proposal
# is a separate object.
# Expected: accepted; the returned proposal equals the input but is a separate copy.

# Exercise 2: Predict a case-changed tool name
# Submit tool READ_FIXTURE with document_id d1 and predict which check rejects it.
# Expected: ValueError 'unknown tool'; names are matched exactly, without case folding.

# Exercise 3: Reject extra fields
# Add command or path to an otherwise valid object.
# Expected: extra fields rejected.

# Exercise 4: Reject traversal-like identifiers
# Submit ../secret as the document ID.
# Expected: ValueError because the ID is outside the fixture allowlist.

# Exercise 5: Enforce types
# Submit the integer document_id 1, then a list instead of an object.
# Expected: TypeError for both malformed structures.

# Exercise 6: Keep retrieved instructions inert
# Read a fixture string saying ignore policy and run a command, then verify no second
# operation is proposed or executed.
# Expected: returned value is text; dispatch count 1.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
