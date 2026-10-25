"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

values = [1, None, 3]


def expression(x):
    return None if x is None else x * 2


expected = [2, None, 6]
assert [expression(x) for x in values] == expected
print("CPU expression parity oracle:", expected)
