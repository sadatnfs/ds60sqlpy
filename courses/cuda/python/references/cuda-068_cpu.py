"""Independent CPU reference with deterministic contract assertions."""

rows = [[1.0, 3.0], [3.0, 7.0]]
means = [sum(row[c] for row in rows) / len(rows) for c in range(2)]
centered = [[x - m for x, m in zip(row, means, strict=True)] for row in rows]
assert centered == [[-1.0, -2.0], [1.0, 2.0]]
x, y = [1, 2], [4, 6]
distance = sum((a - b) ** 2 for a, b in zip(x, y, strict=True))
assert distance == 25
print("CPU array reference:", centered, distance)
