"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

values = [3, 6, 9]
clamped = [
    (values[max(0, i - 1)] + values[i] + values[min(len(values) - 1, i + 1)]) / 3
    for i in range(len(values))
]
assert clamped == [4, 6, 8]
assert 1 * 3 + 2 == 5
print("CPU image reference:", clamped)
