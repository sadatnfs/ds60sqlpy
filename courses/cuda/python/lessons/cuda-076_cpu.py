"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

tile = [2, 4, 6]
width = 4
shared = [tile[i] if i < len(tile) else 0 for i in range(width)]
participants = list(range(width))
assert participants == [0, 1, 2, 3]
assert sum(shared) == 12
print("CPU cooperative model:", shared, sum(shared))
