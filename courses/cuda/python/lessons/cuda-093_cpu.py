"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

shapes = [(4, 8), (4, 8), (8, 8)]
assert len(set(shapes)) == 2
compile_ms, saving_ms = 500, 1
assert compile_ms / saving_ms == 500
print("CPU compilation model:", len(set(shapes)), "specializations; break-even", 500)
