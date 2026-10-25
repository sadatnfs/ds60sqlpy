"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

values = [0, 0, 1, 2, 2, 2]
bins = [0] * 3
for value in values:
    bins[value] += 1
left, right = [2, 1, 0], [0, 0, 3]
merged = [a + b for a, b in zip(left, right, strict=True)]
assert bins == merged == [2, 1, 3]
print("CPU histogram oracle:", bins)
