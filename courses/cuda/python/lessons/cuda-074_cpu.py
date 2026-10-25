"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

n, block = 10, 4
blocks = (n + block - 1) // block
visits = [b * block + t for b in range(blocks) for t in range(block) if b * block + t < n]
assert visits == list(range(n))
strided = [i for t in range(6) for i in range(t, 14, 6)]
assert sorted(strided) == list(range(14))
print("CPU indexing model:", visits)
