"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

rows = [("A", 2), ("A", 4), ("B", 6), ("B", 8)]
totals = {}
for key, value in rows:
    totals[key] = totals.get(key, 0) + value
assert totals == {"A": 6, "B": 14}
print("CPU Spark semantic oracle:", sorted(totals.items()))
