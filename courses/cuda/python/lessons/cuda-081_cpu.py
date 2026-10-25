"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

owner = [1, 2, 3]
alias = owner
copied = list(owner)
alias[0] = 9
assert owner == [9, 2, 3]
assert copied == [1, 2, 3]
print("CPU alias reference:", owner, copied)
