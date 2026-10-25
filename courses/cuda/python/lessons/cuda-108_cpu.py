"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

rows = [("A", 2), ("A", None), ("B", 5)]
totals = {}
counts = {}
for key, value in rows:
    totals.setdefault(key, 0)
    counts[key] = counts.get(key, 0) + 1
    if value is not None:
        totals[key] += value
assert totals == {"A": 2, "B": 5} and counts["A"] == 2
print("CPU dataframe oracle:", totals, counts)
