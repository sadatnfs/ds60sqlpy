"""Independent CPU reference with deterministic contract assertions."""

left = [("A", 1), ("A", 2), ("B", 3)]
right = [("A", 10), ("A", 20), ("C", 30)]
joined = [(k, a, b) for k, a in left for r, b in right if k == r]
assert len(joined) == 4
assert {k for k, _, _ in joined} == {"A"}
print("CPU join oracle:", joined)
