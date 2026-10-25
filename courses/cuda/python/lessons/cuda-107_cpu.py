"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

records = [(2, "A"), (1, "B"), (2, "C")]
ordered = sorted(records, key=lambda row: row[0])
assert ordered == [(1, "B"), (2, "A"), (2, "C")]
a, b = (2, 3), (3, 4)
assert a[1] == b[0]
print("CPU library contracts:", ordered, "matrix output", (a[0], b[1]))
