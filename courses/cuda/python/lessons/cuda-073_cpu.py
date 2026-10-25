"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""


def affine_reference(values, scale):
    return [scale * x for x in values]


assert affine_reference([1, -2, 3], 2) == [2, -4, 6]
assert affine_reference([], 2) == []
print("CPU kernel oracle:", affine_reference([1, -2, 3], 2))
