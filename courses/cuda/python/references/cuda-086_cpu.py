"""Independent CPU reference with deterministic contract assertions."""

rows = [[1, 2], [3, 4]]
means = [sum(row[c] for row in rows) / len(rows) for c in range(2)]
centered = [[x - m for x, m in zip(row, means, strict=True)] for row in rows]
scores = [sum(x * w for x, w in zip(row, [2, -1], strict=True)) for row in centered]
assert means == [2, 3] and scores == [-1, 1]
print("CPU pipeline oracle:", means, scores)
