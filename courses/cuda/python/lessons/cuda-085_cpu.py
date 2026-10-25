"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

library = {"kernel": 8, "transfer": 2, "packing": 0}
custom = {"kernel": 6, "transfer": 2, "packing": 3}
assert sum(library.values()) == 10
assert sum(custom.values()) == 11
print("CPU decision model: library", sum(library.values()), "custom", sum(custom.values()))
