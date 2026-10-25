"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""


def offset(indices, strides):
    return sum(i * s for i, s in zip(indices, strides, strict=True))


assert offset((1, 2), (12, 4)) == 20
assert offset((1, 1), (12, 8)) == 20
assert offset((2, 1), (4, 12)) == 20
print("CPU layout model:", offset((1, 2), (12, 4)), "bytes")
