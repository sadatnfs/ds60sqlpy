"""Independent CPU reference with deterministic contract assertions."""

records = [(2, "A"), (1, "B"), (2, "C")]
ordered = sorted(records, key=lambda row: row[0])
assert ordered == [(1, "B"), (2, "A"), (2, "C")]
a, b = (2, 3), (3, 4)
assert a[1] == b[0]
print("CPU library contracts:", ordered, "matrix output", (a[0], b[1]))
