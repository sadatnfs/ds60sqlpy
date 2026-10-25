"""Independent CPU reference with deterministic contract assertions."""

owner = [1, 2, 3]
alias = owner
copied = list(owner)
alias[0] = 9
assert owner == [9, 2, 3]
assert copied == [1, 2, 3]
print("CPU alias reference:", owner, copied)
