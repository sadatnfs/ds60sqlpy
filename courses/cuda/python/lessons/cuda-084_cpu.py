"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""


def affine(values):
    return [2 * x + 1 for x in values]


assert affine([-1, 0, 3]) == [-1, 1, 7]
n, threads = 257, 128
assert (n + threads - 1) // threads == 3
assert affine([]) == []
print("CPU raw-kernel oracle:", affine([-1, 0, 3]))
