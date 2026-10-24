"""nlp-003 learner workspace. Inspect actual spans before designing a repair."""

import re

text = "Pay INV-1042, then review INV-9012."
pattern = re.compile(r"\bINV-(?P<number>[0-9]{4})\b")
for match in pattern.finditer(text):
    print(match.group(0), match.group("number"), match.span())

# Exercise 1: Return exact strings, digit groups and source spans.
# Expected: INV-1042 at(4,12), INV-9012 at(26,34), each slice matching the raw text.
# Exercise 2: Reject long, prefixed, underscore-prefixed and non-ASCII-digit cases.
# Expected: four negative fixtures rejected; parenthesized valid ID retained.
# Exercise 3: Compare search, match and fullmatch for messages and ID-only fields.
# Expected: True,False,True,False for the guide's four calls.
# Exercise 4: Accept ordinary ASCII prefix case and exclude all-zero numbers.
# Expected: inv-7777 canonicalized to INV-7777 at(10,18) in the third example.
# Exercise 5: Calculate exact entity TP/FP/FN, retaining document identity.
# Expected:2/1/1 and precision=recall=2/3; changing document identity breaks a match.
# Exercise 6: Explain why a matching mention cannot authorize an action.
# Expected: two contrasting messages and explicit missing semantic/authorization evidence.
# Add your implementations, assertions and explanation below.
